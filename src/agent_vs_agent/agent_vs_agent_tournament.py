import sys
import multiprocessing

# logger
from src.logger.logger import setup_logger

logger = setup_logger(__name__)

from tqdm import tqdm

from src.consts import PYBIND_DIR

sys.path.append(str(PYBIND_DIR))

import snake_lib

import sys


# Game configurations
n_snakes = 2
n_apples = 5
board_width = 10
board_height = 10

def _play_one_game_task(args_tuple):

    from src.consts import PYBIND_DIR
    sys.path.append(str(PYBIND_DIR))
    import snake_lib

    # Unpack arguments
    agent_0_type, agent_1_type, AGENT_0_IDX, AGENT_1_IDX, \
    n_snakes_config, n_apples_config, board_width_config, board_height_config = args_tuple

    # Each worker process creates its own C++ object instances
    agent = snake_lib.Agent()
    state = snake_lib.State(n_snakes_config, n_apples_config, board_width_config, board_height_config)

    while not state.is_game_over():

            
        # python is snake 1
        snake_moving_idx = state.turn % n_snakes

        if snake_moving_idx == AGENT_1_IDX:

            if agent_1_type == "mcts":
                direction = agent.mcts_based_agent(state, AGENT_1_IDX, 1000)
            elif agent_1_type == "minimax":
                direction = agent.minimax_based_agent(state, AGENT_1_IDX, 8)
            elif agent_1_type == "bfs":
                direction = agent.bfs_based_agent(state, AGENT_1_IDX)
            elif agent_1_type == "random":
                direction = agent.random_based_agent(state, AGENT_1_IDX)
            else:
                raise Exception("Incorrect agent")

            # given direction move
            state.move(direction, AGENT_1_IDX)
        
        else:

            if agent_0_type == "mcts":
                direction = agent.mcts_based_agent(state, AGENT_0_IDX, 1000)
            elif agent_0_type == "minimax":
                direction = agent.minimax_based_agent(state, AGENT_0_IDX, 8)
            elif agent_0_type == "bfs":
                direction = agent.bfs_based_agent(state, AGENT_0_IDX)
            elif agent_0_type == "random":
                direction = agent.random_based_agent(state, AGENT_0_IDX)
            else:
                raise Exception("Incorrect agent")

            # given direction move
            state.move(direction, AGENT_0_IDX)

    if len(state.snakes[AGENT_0_IDX].tail) > len(state.snakes[AGENT_1_IDX].tail):
        return AGENT_0_IDX, state.turn
    else:
        return AGENT_1_IDX, state.turn




class Tournament:
    """Allows us to check which agent is better oveall"""
    def __init__(self, agent_name_0: str, agent_name_1: str):
        self.agent_0_type = agent_name_0
        self.agent_1_type = agent_name_1
        self.stats = {agent_name_0: 0, agent_name_1: 0, "turns": []}

        
    
    def run_tournament(self, tournament_amount: int):
        # AGENT_1_IDX = random.choice([0, 1])
        # AGENT_0_IDX = 1 if MODEL_IDX == 0 else 0
        AGENT_0_IDX = 0
        AGENT_1_IDX = 1

        tasks_args = []
        for _ in range(tournament_amount):
            tasks_args.append((
                self.agent_0_type, self.agent_1_type,
                AGENT_0_IDX, AGENT_1_IDX,
                n_snakes, n_apples, board_width, board_height
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
                a0, a1 =0, 0
                for i, t in results_from_pool:
                    if i == AGENT_0_IDX:
                        a0 += 1
                    else:
                        a1 += 1
                # logger.debug(f"Current results: {self.agent_0_type} wins: {a0}, {self.agent_1_type} wins: {a1}")
        # Process results
        for winner_idx, turns in results_from_pool:
           
            if winner_idx == AGENT_0_IDX:
                self.stats[self.agent_0_type] += 1
            else:
                self.stats[self.agent_1_type] += 1
            
            self.stats["turns"].append(turns)
        


if __name__ == "__main__":
    multiprocessing.freeze_support() 

    manager = Tournament("minimax", "bfs")

    tournament_games = 50
    logger.info(f"Starting tournament with {tournament_games} games...")
    manager.run_tournament(tournament_amount=tournament_games)

    logger.info("Tournament finished. Results:")
    logger.info(manager.stats)
