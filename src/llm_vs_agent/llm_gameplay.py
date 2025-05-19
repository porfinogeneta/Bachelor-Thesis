
from src.llm_vs_agent.game_visualizer import GameVisualizer
import subprocess
import os
import re
import random

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


from src.consts import PYBIND_DIR

sys.path.append(str(PYBIND_DIR))

import snake_lib

import argparse
import sys


# Game configurations
n_snakes = 2
n_apples = 5
board_width = 10
board_height = 10

def main(model_name: str, sample_valid_tokens: bool, device: str, agent_type: str = "random_agent"):
    """
    Runs the snake game simulation using the C++ classes exposed via pybind11 and language model.

    returns the amount of improper generations and string literal llm, agent on game over
    """

    parser = argparse.ArgumentParser(description="Run the Snake game simulation.")
    parser.add_argument('-V', '--visualize', action='store_true', help='Enable game visualization')

    args = parser.parse_args()

    visualize = args.visualize

    

    # llm caller
    caller = LLMCaller(model_name=model_name, device=device)

    game_sequence = "<START> "
   
    # Create instances of the C++ State and Agent classes
    state = snake_lib.State(n_snakes, n_apples, board_width, board_height)
    agent = snake_lib.Agent()

    # MODEL_IDX = random.choice([0, 1])
    # AGENT_IDX = 1 if MODEL_IDX == 0 else 0
    MODEL_IDX = 0
    AGENT_IDX = 1

    # initialize both snakes
    game_sequence += f"S0 R{state.snakes[0].head[0]}C{state.snakes[0].head[1]} L{len(state.snakes[0].tail)} "
    game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "
    game_sequence += f"S1 R{state.snakes[1].head[0]}C{state.snakes[1].head[1]} L{len(state.snakes[1].tail)} "
    game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "



    # counter of improper moves generation of a model
    improper_genenerations_cnt = 0

    # visualize = False

    if visualize:
        # game visualizer
        visualizer = GameVisualizer(model_idx=MODEL_IDX)

    

    while not state.is_game_over():

        if visualize:
            visualizer.visualize_state(state)

        # the game cannot be longer than 800 turns, in this case longer snake wins, regardless of the other being alive
        if state.turn > 800:
             if len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MODEL_IDX].tail):
                 return improper_genenerations_cnt, "agent", state
             else:
                 return improper_genenerations_cnt, "model", state

        # agent's snake is longer and llm's is dead, no point of further gameplay
        if len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MODEL_IDX].tail) and (MODEL_IDX in state.eliminated_snakes):
            return improper_genenerations_cnt, "agent", state
        # llm's is longer and agent's is dead
        elif len(state.snakes[MODEL_IDX].tail) > len(state.snakes[AGENT_IDX].tail) and (AGENT_IDX in state.eliminated_snakes):
            return improper_genenerations_cnt, "model", state
            
        # python is snake 1
        snake_moving_idx = state.turn % n_snakes

        if snake_moving_idx == MODEL_IDX:

            # print("Python turn")

            # snake was eleminated not need for any generation, skip the turn
            if MODEL_IDX in state.eliminated_snakes:
                state.turn += 1
                continue

            prev_head = state.snakes[MODEL_IDX].head

            if sample_valid_tokens:

                batch_moves, ict, cnt = caller.sample_next_batch_moves_from_legal_tokens(
                    prev_heads=[prev_head], 
                    game_sequences=[f"{game_sequence}S{MODEL_IDX}"],
                    states=[state],
                    language_model_snake_idx=MODEL_IDX
                )

            else:
                batch_moves, ict, cnt = caller.sample_next_batch_moves(
                    prev_heads=[prev_head], 
                    game_sequences=[f"{game_sequence}S{MODEL_IDX}"],
                    top_k=1
                )

            improper_genenerations_cnt += cnt
                    
            if ict != [None]:
                logger.error(ict)

            # given direction move, batch_moves is a lists, hence [0]
            state.move(batch_moves[0], MODEL_IDX)

            # add current S_MODEL_IDX position
            game_sequence += f"S{MODEL_IDX} R{state.snakes[MODEL_IDX].head[0]}C{state.snakes[MODEL_IDX].head[1]} L{len(state.snakes[MODEL_IDX].tail)} "
            game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "

        else:

            # print("Cpp turn")

            direction = agent.bfs_based_agent(state, AGENT_IDX)
            # if agent_type == "random_agent":
            #     direction = agent.random_based_agent(state, snake_moving_idx)
            # print(f"Snake {snake_moving_idx} moving: {direction}")

            # given direction move
            state.move(direction, AGENT_IDX)

            # add current S_AGENT_IDX position
            game_sequence += f"S{AGENT_IDX} R{state.snakes[AGENT_IDX].head[0]}C{state.snakes[AGENT_IDX].head[1]} L{len(state.snakes[AGENT_IDX].tail)} "
            game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "


        # print(state.snakes)
        # print(state.snakes[0].tail)
        # print(state.snakes[1].tail)
    
    # agent is snake 0
    if len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MODEL_IDX].tail):
        return improper_genenerations_cnt, "agent", state
    else:
        return improper_genenerations_cnt, "model", state
        


if __name__ == "__main__":
    print(main(model_name="out_standard_positions_bs_128", sample_valid_tokens=True, device="cuda"))