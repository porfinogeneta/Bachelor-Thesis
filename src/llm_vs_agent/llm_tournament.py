
from llm_vs_agent.game_visualizer import GameVisualizer
import subprocess
import os
import re
import random
from dataclasses import dataclass

import sys
import os
# visualizer
# from src.snake_game.game_visualizer import GameVisualizer
from src.llm_vs_agent.game_visualizer import GameVisualizer

# llm caller
from src.llm_vs_agent.llm_caller import LLMCaller

# logger
from src.logger.logger import setup_logger

logger = setup_logger(__name__)

# cpp code
module_path = '/Users/szymon/Documents/Bachelor-Thesis/python_cpp_binding/'
# module_path = "/home/ubuntu/Bachelor-Thesis/python_cpp_binding/"

sys.path.append(module_path)
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

    def __init__(self, model_name: str, n_tournaments: int, batch_size: int):
        self.n_tournaments = n_tournaments
        self.batch_size= batch_size
        self.games = []
        self.agent = snake_lib.Agent()
        self.results = {"model": 0, "agent": 0, "incorrect_generations": 0}
        self.results_per_batch = []
        # dictionary of incorrect tokens paired with the state for which they were generated
        self.incorrect_token_paired_with_state = []
        self.llm_caller = LLMCaller(model_name=model_name)
    
    def initialize_game(self, game_id: int):
        """Initialize game and add it to games list"""

        

        # each new game needs a new state
        state = snake_lib.State(n_snakes, n_apples, board_width, board_height)
        
        game_sequence = "<START> "

        
        # initialize both snakes
        game_sequence += f"S0 R{state.snakes[0].moves_history[0][0]}C{state.snakes[0].moves_history[0][1]} L{len(state.snakes[0].tail)} "
        game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "
        game_sequence += f"S1 R{state.snakes[1].head[0]}C{state.snakes[1].head[1]} L{len(state.snakes[1].tail)} "
        game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "
        
        self.games.append(GameState(
            game_id=game_id,
            state=state,
            game_sequence=game_sequence,
            prev_head=state.snakes[1].head,
            improper_generations=0,
        ))


    def run_unpadded_tournaments(self, output_file: str, sample_valid_tokens: bool = False):
        """
            This is the easiest implementation, where batch feeded to the model
            decreases in size as the games keep on ending
        """
        batch_idx = 0

        # run games batch by batch
        # batch size is effectively the biggest amount of games played at once
        while batch_idx < self.n_tournaments / self.batch_size:
            
            # initialize batch size of games
            # reset games list
            self.games = []
            for i in range(self.batch_size):
                self.initialize_game(game_id=i)

            active_games = list(range(self.batch_size))

            # in every batch choose at random which snake is model and which is an agent
            MODEL_IDX = random.choice([0, 1])
            AGENT_IDX = 1 if MODEL_IDX == 0 else 0

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

                    # logger.info(state.print_game_state())

                    # CHECK END GAME
                    if state.is_game_over():
                        # Determine winner
                        if len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MODEL_IDX].tail):
                            batch_scores["agent"] += 1
                        else:
                            batch_scores["model"] += 1
                        
                        games_to_remove.append(game_id)
                    
                    # agent's snake is longer and llm's is dead
                    elif len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MODEL_IDX].tail) and (MODEL_IDX in state.eliminated_snakes):
                        batch_scores["agent"] += 1
                        games_to_remove.append(game_id)
                    # llm's is longer and agent's is dead
                    elif len(state.snakes[MODEL_IDX].tail) > len(state.snakes[AGENT_IDX].tail) and (AGENT_IDX in state.eliminated_snakes):
                        batch_scores["model"] += 1
                        games_to_remove.append(game_id)
                
                # Remove games that are over
                for id in games_to_remove:
                    active_games.remove(id)
                
                # If no active games left, break
                if active_games == []:
                    break

                # APPLY BATCH TURN
                # Determine current batch turn (0 for agent, 1 for LLM)
                batch_turn = self.games[active_games[0]].state.turn % n_snakes

                # logger.error(len(set([turn for i in range(len(active_games)) for turn in self.games[active_games[i]].state.turn])))

                # Process agent's turn (batch_turn = AGENT_IDX)
                # each batch have assigned MODEL_IDX and AGENT_IDX
                if batch_turn == AGENT_IDX:
                    for game_id in active_games:
                        game = self.games[game_id]
                        state = game.state
                        
                        # Skip if agent's snake is eliminated
                        if AGENT_IDX in state.eliminated_snakes:
                            state.turn += 1
                            apple_positions = ' '.join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples])
                            # dead snake gets S_AGENT_IDX <DEAD> L10 A12A23A34A35A36 
                            game.game_sequence += f"S{AGENT_IDX} <DEAD> L{len(state.snakes[0].tail)} {apple_positions} "
                            continue
                            
                        direction = self.agent.bfs_based_agent(state, AGENT_IDX)
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

                            # states and incorrect tokens that were generated for them
                            if incorrect_tokens[i] != None:
                                self.incorrect_token_paired_with_state.append((batch_idx, incorrect_tokens[i], state))
                            
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
            file.write(f"{self.results}\n")


            batch_res = ""
            for result_batch in self.results_per_batch:
                batch_res += f'Batch: {result_batch["batch_number"]}/{self.n_tournaments // self.batch_size}\nResult: {result_batch}\n\n'

            file.write(batch_res)

            file.write("Improper Moves:\n\n")
            # - Model is S{self.results_per_batch[batch_idx-1]['model_idx']}
            for batch_idx, incorrect_token, incorrect_state in self.incorrect_token_paired_with_state:
                file.write(f"TOKEN: {incorrect_token}\n")
                file.write(f"Batch index: {batch_idx}\n")
                file.write(f"{incorrect_state.get_game_state()}\n\n")


        # logger.info(self.results)

        # for batch_idx, incorrect_token, incorrect_state in self.incorrect_token_paired_with_state:
        #     logger.info(f"TOKEN: {incorrect_token}")
        #     logger.info(f"Batch index: {batch_idx} - Model is S{self.results_per_batch[batch_idx-1]['model_idx']}")
        #     logger.info(f"{incorrect_state.get_game_state()}")

if __name__ == "__main__":
   manager = TournamentManager(model_name="out-standard_pos_1774_ctx_bs_64_baby",
                                n_tournaments=10,
                                batch_size=5)

   manager.run_unpadded_tournaments(output_file="tournamnets_results.txt", sample_valid_tokens=False)