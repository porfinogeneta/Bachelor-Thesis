
# from llm_vs_agent.game_visualizer import GameVisualizer
import subprocess
import os
import re
import random
from dataclasses import dataclass
import pathlib

import sys
import os

# llm caller
from src.llm_vs_agent.llm_caller import LLMCaller

# logger
from src.logger.logger import setup_logger

logger = setup_logger(__name__)

from src.consts import PYBIND_DIR, PROJECT_PATH
sys.path.append(str(PYBIND_DIR))
import snake_lib

import argparse
import sys


# Game configurations
n_snakes = 2
n_apples = 5
board_width = 10
board_height = 10

@dataclass
class GameState:
    game_id: int
    state: any  # snake_lib.State
    game_sequence: str
    prev_head: tuple
    improper_generations: int


class TournamentManager:

    def __init__(self, model_name: str, corpora_type: str, device: str, n_tournaments: int, batch_size: int):
        self.n_tournaments = n_tournaments
        self.batch_size= batch_size
        self.corpora_type = corpora_type
        self.games = []
        self.agent = snake_lib.Agent()
        self.results = {"model": 0, "agent": 0, "incorrect_generations": 0}
        self.results_per_batch = []
        # dictionary of incorrect tokens paired with the state for which they were generated
        self.incorrect_token_paired_with_state = []
        self.llm_caller = LLMCaller(model_name=model_name, device=device)
    
    def initialize_game(self, game_id: int, batch_model_id: int):
        """Initialize game and add it to games list"""

        

        # each new game needs a new state
        state = snake_lib.State(n_snakes, n_apples, board_width, board_height)
        
        game_sequence = "<START> "

        
        # initialize both snakes
        game_sequence += f"S0 R{state.snakes[0].head[0]}C{state.snakes[0].head[1]} L{len(state.snakes[0].tail)} "
        game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "
        game_sequence += f"S1 R{state.snakes[1].head[0]}C{state.snakes[1].head[1]} L{len(state.snakes[1].tail)} "
        game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "

        # cpy = self.create_game_sequence("", None, state)
        # assert cpy == game_sequence, "Created sequence should be the same"
        
        self.games.append(GameState(
            game_id=game_id,
            state=state,
            game_sequence=game_sequence,
            prev_head=state.snakes[batch_model_id].head,
            improper_generations=0,
        ))


    def create_game_sequence(self, game_sequence: str, prev_state: snake_lib.State, current_state: snake_lib.State):
        """
            Game sequence should be created based on model type, since each model may accept different game sequence
        """
        if self.corpora_type == "standard_positions":

            # initializing sequence
            if prev_state == None:
                assert game_sequence == "", "At the beginning game sequence shouldn't be empty"
                game_sequence = "<START> "
                game_sequence += f"S0 R{current_state.snakes[0].head[0]}C{current_state.snakes[0].head[1]} L{len(current_state.snakes[0].tail)} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples]) + " "
                game_sequence += f"S1 R{current_state.snakes[1].head[0]}C{current_state.snakes[1].head[1]} L{len(current_state.snakes[1].tail)} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples]) + " "
                return game_sequence

            # get snake, for which sequence needs to be created
            currently_moving_snake_idx = current_state.turn % current_state.n_snakes
            # current snake is dead, return dead sequence if this happens
            if currently_moving_snake_idx in current_state.eliminated_snakes:
                apple_positions = ' '.join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples])
                # dead snake gets S_AGENT_IDX <DEAD> L10 A12A23A34A35A36 
                game_sequence += f"S{currently_moving_snake_idx} <DEAD> L{len(current_state.snakes[currently_moving_snake_idx].tail)} {apple_positions} "
                return game_sequence
            # normal sequence filling
            else:
                game_sequence += f"S{currently_moving_snake_idx} R{current_state.snakes[currently_moving_snake_idx].head[0]}C{current_state.snakes[currently_moving_snake_idx].head[1]} L{len(current_state.snakes[currently_moving_snake_idx].tail)} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples]) + " "
                return game_sequence


        elif self.corpora_type == "apples_corpora":
            pass
        else:
            raise Exception("Incorrect Corpora Type")


    def run_tournaments(self, output_file: str, model_idx: int, sample_valid_tokens: bool = False, agent: str = "bfs"):
        """
            This is the easiest implementation, where batch feeded to the model
            decreases in size as the games keep on ending
        """
        batch_idx = 0

        # run games batch by batch
        # batch size is effectively the biggest amount of games played at once
        while batch_idx < self.n_tournaments / self.batch_size:
            
            if model_idx == 1:
                MODEL_IDX = 1
                AGENT_IDX = 0
            else:
                MODEL_IDX = 0
                AGENT_IDX = 1 
            
            # reset games list
            self.games = []
            for i in range(self.batch_size):
                self.initialize_game(game_id=i, batch_model_id=MODEL_IDX)

            active_games = list(range(self.batch_size))
            

            # save statisitcs for each batch
            batch_scores = {"model": 0, "agent": 0, "incorrect_generations": 0}
            
            # begin a new batch
            batch_idx += 1

            while active_games:
                # logger.info(f"Active Games: {len(active_games)}")
                # First check which games are over
                games_to_remove = []
                for game_id in active_games:
                    game = self.games[game_id]
                    state = game.state


                    # # the game cannot be longer than 800 turns, in this case longer snake wins, regardless of the other being alive
                    # # protection against looping generation
                    # if state.turn > 1000:
                    #     if len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MODEL_IDX].tail):
                    #         batch_scores["agent"] += 1
                    #     else:
                    #         batch_scores["model"] += 1

                    #     games_to_remove.append(game_id)


                    # # # CHECK END GAME
                    # # if state.is_game_over():
                    # #     # Determine winner
                    # #     if len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MODEL_IDX].tail):
                    # #         batch_scores["agent"] += 1
                    # #     else:
                    # #         batch_scores["model"] += 1
                        
                    # #     games_to_remove.append(game_id)
                    
                    # # agent's snake is longer and llm's is dead
                    # elif len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MODEL_IDX].tail) and (MODEL_IDX in state.eliminated_snakes):
                    #     batch_scores["agent"] += 1
                    #     games_to_remove.append(game_id)
                    # # llm's is longer and agent's is dead
                    # elif len(state.snakes[MODEL_IDX].tail) > len(state.snakes[AGENT_IDX].tail) and (AGENT_IDX in state.eliminated_snakes):
                    #     batch_scores["model"] += 1
                    #     games_to_remove.append(game_id)

        
                    # CHECK END GAME
                    if state.is_game_over():
                        # Determine winner
                        if len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MODEL_IDX].tail):
                            batch_scores["agent"] += 1
                        else:
                            batch_scores["model"] += 1
                        
                        games_to_remove.append(game_id)
                
                # Remove games that are over
                for id in games_to_remove:
                    active_games.remove(id)
                
                # If no active games left, break
                if active_games == []:
                    break

                # APPLY BATCH TURN
                # Determine current batch turn
                batch_turn = self.games[active_games[0]].state.turn % n_snakes

                # logger.error(len(set([turn for i in range(len(active_games)) for turn in self.games[active_games[i]].state.turn])))

                # Process agent's turn (batch_turn = AGENT_IDX)
                # each batch have assigned MODEL_IDX and AGENT_IDX
                if batch_turn == AGENT_IDX:
                    for game_id in active_games:
                        game = self.games[game_id]
                        state = game.state

                        assert batch_turn == state.turn % n_snakes, "Batch turn should be the same, as current state turn"
                        
                        # Skip if agent's snake is eliminated
                        if AGENT_IDX in state.eliminated_snakes:
                            state.turn += 1
                            apple_positions = ' '.join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples])
                            # dead snake gets S_AGENT_IDX <DEAD> L10 A12A23A34A35A36 
                            cpy = game.game_sequence

                            # self.create_game_sequencecreate_game_sequence(cpy, state, state):
                            game.game_sequence += f"S{AGENT_IDX} <DEAD> L{len(state.snakes[AGENT_IDX].tail)} {apple_positions} "
                            continue
                        

                        if agent == "bfs":
                            direction = self.agent.bfs_based_agent(state, AGENT_IDX)
                        elif agent == "random":
                            direction = self.agent.random_based_agent(state, AGENT_IDX)
                        
                        state.move(direction, AGENT_IDX)
                        
                        game.state = state
                        # add current S_AGENT_IDX position
                        game.game_sequence += f"S{AGENT_IDX} R{state.snakes[AGENT_IDX].head[0]}C{state.snakes[AGENT_IDX].head[1]} L{len(state.snakes[AGENT_IDX].tail)} "
                        game.game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "
                        

                # Process LLM's turn (batch_turn = MODEL_IDX)
                else:
                    # Prepare batches for LLM moves
                    game_sequences = []
                    prev_heads = []
                    active_llm_games = []
                    states = []
                    
                    for game_id in active_games:
                        game = self.games[game_id]
                        state = game.state
                        
                        # Skip if LLM's snake is eliminated
                        if MODEL_IDX in state.eliminated_snakes:
                            state.turn += 1
                            continue
                        
                        prev_head = state.snakes[MODEL_IDX].head
                        game_sequences.append(f"{game.game_sequence}S{MODEL_IDX}")
                        prev_heads.append(prev_head)
                        active_llm_games.append(game_id)
                        states.append(state)
                    
                    # Only call LLM if there are active games for it
                    if active_llm_games:
                        if sample_valid_tokens == False:
                            
                            batch_moves, incorrect_tokens, incorrect_generations = self.llm_caller.sample_next_batch_moves(
                                prev_heads=prev_heads, 
                                game_sequences=game_sequences
                            )
                            # logger.info(batch_moves)
                        else:
                            batch_moves, incorrect_tokens, incorrect_generations = self.llm_caller.sample_next_batch_moves_from_legal_tokens(
                                prev_heads=prev_heads, 
                                game_sequences=game_sequences,
                                states=states,
                                language_model_snake_idx=MODEL_IDX,
                            )

                        # incorrect generations in one sampling
                        batch_scores["incorrect_generations"] += incorrect_generations

                        
                        # logger.info(f"left in batch: {len(batch_moves)}")
                        
                        # Apply LLM moves to each corresponding game
                        for i, direction in enumerate(batch_moves):
                            game_id = active_llm_games[i]
                            game = self.games[game_id]
                            state = game.state

                            state_cpy = state.deepCopy()

                            # states and incorrect tokens that were generated for them
                            if incorrect_tokens[i] != None:
                                self.incorrect_token_paired_with_state.append((batch_idx, batch_turn, MODEL_IDX, incorrect_tokens[i], state_cpy))
                            
                            state.move(direction, MODEL_IDX)
                            
                            # add current S1 position
                            game.game_sequence += f"S{MODEL_IDX} R{state.snakes[MODEL_IDX].head[0]}C{state.snakes[MODEL_IDX].head[1]} L{len(state.snakes[MODEL_IDX].tail)} "
                            game.game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "
                            
            
            # no active games, end of batch
            self.results_per_batch.append({"batch_number": batch_idx, "model_idx": MODEL_IDX, "agent": batch_scores["agent"], "model": batch_scores["model"], "incorrect_generations": batch_scores["incorrect_generations"]})
            
            self.results["model"] += batch_scores["model"]
            self.results["agent"] += batch_scores["agent"]
            self.results["incorrect_generations"] += batch_scores["incorrect_generations"]

            logger.info(f"Batch: {batch_idx}/{self.n_tournaments // self.batch_size}\nResult: {batch_scores}\nModel is S{MODEL_IDX}\n")      
        
        with open(output_file, "w") as file:
            file.write(f"{self.results}\n\n")


            batch_res = ""
            for result_batch in self.results_per_batch:
                batch_res += f'Batch: {result_batch["batch_number"]}/{self.n_tournaments // self.batch_size}\nResult: {result_batch}\n\n'

            file.write(batch_res)

            file.write("="*50)

            file.write("\n")
            # incorrect generation can be divided into situations where correct generation was impossible
            # and situations where model just broke down and generated invlid tokens
            # in the former situation we won't count it as improper generation

            bad_generations = []
            no_choice_generations = []

            # - Model is S{self.results_per_batch[batch_idx-1]['model_idx']}
            for batch_idx, batch_turn, model_idx, incorrect_token, incorrect_state in self.incorrect_token_paired_with_state:
                
                # illegal move where no space was left shouldn't count as illegal move
                snake = incorrect_state.snakes[model_idx]
                were_there_options = False
                for d in "UDLR":
                    if incorrect_state.try_move(d, snake) == True:
                        # logger.error(d)
                        # logger.error(model_idx)
                        # logger.error(incorrect_state.get_game_state())
                        were_there_options = True
                        break
                
                if were_there_options:
                    bad_generations.append((batch_idx, batch_turn, model_idx, incorrect_token, incorrect_state))
                else:
                    no_choice_generations.append((batch_idx, batch_turn, model_idx, incorrect_token, incorrect_state))
            
            file.write("="*50)
            file.write(f"\nBAD GENERATIONS: {len(bad_generations)}\n")
            for batch_idx, batch_turn, model_idx, incorrect_token, incorrect_state in bad_generations:
                file.write(f"TOKEN: {incorrect_token}\n")
                file.write(f"Batch index: {batch_idx}\nBatch Turn: {batch_turn}\nModel is {model_idx}\n\n")
                file.write(f"{incorrect_state.get_game_state()}\n\n")

            file.write("="*50)
            file.write(f"\nNO CHOICE GENERATIONS: {len(no_choice_generations)}\n")
            for batch_idx, batch_turn, model_idx, incorrect_token, incorrect_state in no_choice_generations:
                file.write(f"TOKEN: {incorrect_token}\n")
                file.write(f"Batch index: {batch_idx}\nBatch Turn: {batch_turn}\nModel is {model_idx}\n\n")
                file.write(f"{incorrect_state.get_game_state()}\n\n")



            
        # logger.info(self.results)

        # for batch_idx, incorrect_token, incorrect_state in self.incorrect_token_paired_with_state:
        #     logger.info(f"TOKEN: {incorrect_token}")
        #     logger.info(f"Batch index: {batch_idx} - Model is S{self.results_per_batch[batch_idx-1]['model_idx']}")
        #     logger.info(f"{incorrect_state.get_game_state()}")

if __name__ == "__main__":

    # script for finding the best approach for defating each agent
    TESTING_PATH = pathlib.Path("src/llm_vs_agent/tournaments")
    #, "out_standard_positions_bs_64", "out_standard_positions_bs_128", "out_standard_positions_bs_1600", "out_standard_positions_bs_8000"
    #, "aligned_games/out_aligned_bs_2240", "aligned_games/out_aligned_bs_512"
    MODELS = ["standard_positions_fixed_start/out_fixed_bs_4352"]

    # MODELS = ["out_standard_positions_bs_64"]

    AGENTS = ["bfs"]
    # AGENTS = ["bfs"]

    SAMPLE = ["no-sampling", "sampling"]
    # SAMPLE = ["sampling", "no-sampling"]

    MODEL_IDX = [0, 1]

    for model_name in MODELS:
        for agent_type in AGENTS:

            for do_sample in SAMPLE:

                for model_idx in MODEL_IDX:
                    
                    logger.info(f"Agent {agent_type}")
                    logger.info(f"Sampling? {do_sample}")
                    logger.info(f"Index {model_idx}")

                    manager = TournamentManager(model_name=model_name,
                                                corpora_type="standard",
                                                device="cuda",
                                                    n_tournaments=1000,
                                                    batch_size=500)

                    #    manager.run_unpadded_tournaments(output_file="tournamnets_results_legal_tokens_only.txt", sample_valid_tokens=True)
                    output_directory = PROJECT_PATH / TESTING_PATH / model_name / agent_type / do_sample / f"model_idx_{model_idx}"
                    output_directory.mkdir(parents=True, exist_ok=True)
                    
                    OUTPUT_FILE = output_directory / "tournaments_results.txt"

                    sample = True if do_sample == "sampling" else False

                    manager.run_tournaments(output_file=str(OUTPUT_FILE), sample_valid_tokens=sample, agent=agent_type, model_idx=model_idx)



    # manager = TournamentManager(model_name="out_standard_positions_bs_128",
    #                         device="cuda",
    #                             n_tournaments=1000,
    #                             batch_size=250)

    # #    manager.run_unpadded_tournaments(output_file="tournamnets_results_legal_tokens_only.txt", sample_valid_tokens=True)

    # manager.run_unpadded_tournaments(output_file="/home/ubuntu/Bachelor-Thesis/src/llm_vs_agent/tournaments/out_standard_positions_bs_128/bfs/valid/tournaments_resut_mode_idx_1.txt", sample_valid_tokens=True)