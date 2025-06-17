import sys
import multiprocessing

# logger
from src.logger.logger import setup_logger

from src.consts import STANDARD, APPLES_CORPORA, NO_TAILS, MINIMAL

logger = setup_logger(__name__)

from tqdm import tqdm



import sys

from src.lm_vs_agent.utils import create_game_sequence

from src.gpt_vs_lm.prompts import DEFAULT_PROMPT


# llm caller
from src.lm_vs_agent.lm_caller import LLMCaller
# gpt caller
from src.gpt_vs_lm.gpt_caller import GPTCaller


# Game configurations
n_snakes = 2
n_apples = 5
board_width = 10
board_height = 10

def _play_one_game_task(args_tuple):

    from src.consts import PYBIND_DIR
    sys.path.append(str(PYBIND_DIR))
    import snake_lib

    agent = snake_lib.Agent()

   

    model_name, corpora_type, AGENT_0_IDX, AGENT_1_IDX, n_snakes, n_apples, board_width, board_height, sample_valid_tokens, device = args_tuple



    # Create instances of the C++ State and Agent classes
    state = snake_lib.State(n_snakes, n_apples, board_width, board_height)

    # llm caller
    # OUR MODEL IS AGENT_0
    caller = LLMCaller(model_name=model_name, device=device)
    # AGENT_1 is the GPT model
    gpt_caller = GPTCaller(snake_idx=AGENT_1_IDX)


    # initialize game sequence
    game_sequence = create_game_sequence(corpora_type, "", None, state)


    while not state.is_game_over():


        # python is snake 1
        snake_moving_idx = state.turn % n_snakes

        if snake_moving_idx == AGENT_0_IDX:

            # snake was eleminated not need for any generation, skip the turn
            if AGENT_0_IDX in state.eliminated_snakes:
                state.turn += 1
                continue
            
            prev_state = state.deepCopy()
            prev_head = state.snakes[AGENT_0_IDX].head


            batch_moves, ict, _ = caller.sample_next_batch_moves(
                    prev_heads=[prev_head], 
                    game_sequences=[f"{game_sequence}S{AGENT_0_IDX}"],
                    top_k=1
                )

            # if sample_valid_tokens:

            #     batch_moves, ict, _ = caller.sample_next_batch_moves_from_legal_tokens(
            #         prev_heads=[prev_head], 
            #         game_sequences=[f"{game_sequence}S{AGENT_0_IDX}"],
            #         states=[state],
            #         language_model_snake_idx=AGENT_0_IDX
            #     )

            # else:
            #     batch_moves, ict, _ = caller.sample_next_batch_moves(
            #         prev_heads=[prev_head], 
            #         game_sequences=[f"{game_sequence}S{AGENT_0_IDX}"],
            #         top_k=1
            #     )
                    
            if ict != [None]:
                logger.error(ict)

            state.move(batch_moves[0], AGENT_0_IDX)

            game_sequence = create_game_sequence(corpora_type, game_sequence, prev_state, state)

            # direction = agent.random_based_agent(state, AGENT_0_IDX)
            # state.move(direction, AGENT_0_IDX)
        else:

            # CALL GPT HERE
            # board = gpt_caller.create_board(state)
            # logger.debug(board)
            # prompt  = gpt_caller.create_prompt_based_on_state(state)
            # logger.debug(prompt)

            if AGENT_1_IDX in state.eliminated_snakes:
                state.turn += 1
                continue

            prompt = {
                "sys_msg": DEFAULT_PROMPT[0],
                "human_msg": DEFAULT_PROMPT[1],
            }


            direction, _ = gpt_caller.get_gpt_action(prompt=prompt, sample=sample_valid_tokens, state=state)
            
            assert direction is not None, "GPT class malfunction"
            # direction = agent.bfs_based_agent(state, AGENT_IDX)


            # given direction move
            prev_state = state.deepCopy()
            state.move(direction, AGENT_1_IDX)

            game_sequence = create_game_sequence(corpora_type, game_sequence, prev_state, state)
    
    
    # agent is snake 0
    if len(state.snakes[AGENT_0_IDX].tail) > len(state.snakes[AGENT_1_IDX].tail):
        return AGENT_0_IDX, state.turn
    else:
        return AGENT_1_IDX, state.turn
        




class Tournament:
    """Allows us to check which agent is better oveall"""
    def __init__(self, agent_type_0: str, agent_type_1: str):
        self.agent_0_type = agent_type_0
        self.agent_1_type = agent_type_1
        self.stats = {agent_type_0: 0, agent_type_1: 0, "turns": []}

        
    
    def run_tournament(self, model_name: str, corpora_type: str, sample_valid_tokens: bool, device: str, tournament_amount: int):
        # AGENT_1_IDX = random.choice([0, 1])
        # AGENT_0_IDX = 1 if MODEL_IDX == 0 else 0
        AGENT_0_IDX = 1
        AGENT_1_IDX = 0

        tasks_args = []
        for _ in range(tournament_amount):
            tasks_args.append((
                model_name, corpora_type,
                AGENT_0_IDX, AGENT_1_IDX,
                n_snakes, n_apples, board_width, board_height,
                sample_valid_tokens, device
            ))

        results_from_pool = []
        # Determine the number of processes to use. Default is os.cpu_count().
        with multiprocessing.Pool() as pool:
            # Use imap_unordered to get results as they complete, good for tqdm progress.
            # _play_one_game_task must be a top-level function for pickling.
            game_results_iterator = pool.imap_unordered(_play_one_game_task, tasks_args)
            
            logger.info(f"Running {tournament_amount} games in parallel...")
            for result in tqdm(game_results_iterator, total=tournament_amount, desc="Tournament Progress"):
                results_from_pool.append(result)
                a0, a1 = 0, 0
                for winner_idx, turns in results_from_pool:
                    if winner_idx == AGENT_0_IDX:
                        a0 += 1
                    else:
                        a1 += 1
                    
                    logger.debug(f"agent 0: {a0}\nagent 1: {a1}")
        
        # Process results
        for winner_idx, turns in results_from_pool:
           
            if winner_idx == AGENT_0_IDX:
                self.stats[self.agent_0_type] += 1
            else:
                self.stats[self.agent_1_type] += 1
            
            self.stats["turns"].append(turns)
        


if __name__ == "__main__":
    multiprocessing.freeze_support() 

    manager = Tournament(agent_type_0="our_model", agent_type_1="minimax_model")

    tournament_games = 25
    logger.info(f"Starting tournament with {tournament_games} games...")
    manager.run_tournament(model_name="standard_positions/out_standard_positions_bs_4352",
                            corpora_type=STANDARD,
                            sample_valid_tokens=True,
                            device="mps",
                            tournament_amount=tournament_games)

    logger.info("Tournament finished. Results:")
    logger.info(manager.stats)
