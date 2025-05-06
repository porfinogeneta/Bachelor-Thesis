
from src.snake_game.game_visualizer import GameVisualizer
import subprocess
import os
import re
import random

import sys
import os
# visualizer
from src.snake_game.game_visualizer import GameVisualizer

# llm caller
from src.llm_vs_agent.llm_caller import LLMCaller

# logger
from src.logger.logger import setup_logger

logger = setup_logger(__name__)

# cpp code
module_path = '/Users/szymon/Documents/Bachelor-Thesis/cpp/python_cpp_binding/'

sys.path.append(module_path)
import snake_lib

import argparse
import sys


# Game configurations
n_snakes = 2
n_apples = 5
board_width = 10
board_height = 10

def main(model: str, agent_type: str = "random_agent"):
    """
    Runs the snake game simulation using the C++ classes exposed via pybind11 and language model.

    returns the amount of improper generations and string literal llm, agent on game over
    """

    parser = argparse.ArgumentParser(description="Run the Snake game simulation.")
    parser.add_argument('-V', '--visualize', action='store_true', help='Enable game visualization')

    args = parser.parse_args()

    visualize = args.visualize

    

    # llm caller
    caller = LLMCaller()

    game_sequence = "<START> "
   
    # Create instances of the C++ State and Agent classes
    state = snake_lib.State(n_snakes, n_apples, board_width, board_height)
    agent = snake_lib.Agent()

    # initialize both snakes
    game_sequence += f"S0 R{state.snakes[0].moves_history[0][0]}C{state.snakes[0].moves_history[0][1]} L{len(state.snakes[0].tail)} "
    game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "
    game_sequence += f"S1 R{state.snakes[1].head[0]}C{state.snakes[1].head[1]} L{len(state.snakes[1].tail)} "
    game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "

    # counter of improper moves generation of a model
    improper_genenerations_cnt = 0

    visualize = False

    if visualize:
        # game visualizer
        visualizer = GameVisualizer()

    while not state.is_game_over():

        if visualize:
            visualizer.visualize_state(state)

        # # 193 is average gameplay time in turns in our corpora, probably a good estimation of turns
        # # since 20k games were played
        # if state.turn == 193:
        #     # agent is snake 0
        #     if len(state.snakes[0].tail) > len(state.snakes[1].tail):
        #         return improper_genenerations_cnt, "agent", state
        #     else:
        #         return improper_genenerations_cnt, "llm", state

        # agent's snake is longer and llm's is dead, no point of further gameplay
        if len(state.snakes[0].tail) > len(state.snakes[1].tail) and (1 in state.eliminated_snakes):
            return improper_genenerations_cnt, "agent", state
        # llm's is longer and agent's is dead
        elif len(state.snakes[1].tail) > len(state.snakes[0].tail) and (0 in state.eliminated_snakes):
            return improper_genenerations_cnt, "agent", state
            
        # python is snake 1
        snake_moving_idx = state.turn % n_snakes

        if snake_moving_idx == 1:

            # print("Python turn")

            # snake was eleminated not need for any generation, skip the turn
            if snake_moving_idx in state.eliminated_snakes:
                state.turn += 1
                continue

            prev_head = state.snakes[1].head

            move = caller.sample_next_move(prev_head=prev_head, model=model, game_sequence=f"{game_sequence}S1")

            if not move:
                improper_genenerations_cnt += 1
                move = random.choice(['W', 'S', 'A', 'D'])
                logger.error("improper move")
            
            # move = input("Provide move (WSAD) ").upper()

            # for debugging purposes we use WSAD
            if move == "W":
                direction = "U"
            elif move == "A":
                direction = "L"
            elif move == "D":
                direction = "R"
            elif move == "S":
                direction = "D"

            # given direction move
            state.move(direction, snake_moving_idx)

            # add current S1 position
            game_sequence += f"S1 R{state.snakes[1].head[0]}C{state.snakes[1].head[1]} L{len(state.snakes[1].tail)} "
            game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "

        else:

            # print("Cpp turn")

            direction = agent.bfs_based_agent(state, snake_moving_idx)
            # if agent_type == "random_agent":
            #     direction = agent.random_based_agent(state, snake_moving_idx)
            # print(f"Snake {snake_moving_idx} moving: {direction}")

            # given direction move
            state.move(direction, snake_moving_idx)

            # add current S0 position
            game_sequence += f"S0 R{state.snakes[0].head[0]}C{state.snakes[0].head[1]} L{len(state.snakes[0].tail)} "
            game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "


        # print(state.snakes)
        # print(state.snakes[0].tail)
        # print(state.snakes[1].tail)
    
    # agent is snake 0
    if len(state.snakes[0].tail) > len(state.snakes[1].tail):
        return improper_genenerations_cnt, "agent", state
    else:
        return improper_genenerations_cnt, "llm", state
        


if __name__ == "__main__":
    main(model="out-standard_pos")