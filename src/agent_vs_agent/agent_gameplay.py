
from src.llm_vs_agent.game_visualizer import GameVisualizer

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

def main():
    """
    Runs the snake game simulation using the C++ classes exposed via pybind11 and language model.

    returns the amount of improper generations and string literal llm, agent on game over
    """

    parser = argparse.ArgumentParser(description="Run the Snake game simulation.")
    parser.add_argument('-V', '--visualize', action='store_true', help='Enable game visualization')

    args = parser.parse_args()

    visualize = args.visualize

    # Create instances of the C++ State and Agent classes
    state = snake_lib.State(n_snakes, n_apples, board_width, board_height)
    agent = snake_lib.Agent()

    # MCTS_IDX = random.choice([0, 1])
    # AGENT_IDX = 1 if MODEL_IDX == 0 else 0
    MCTS_IDX = 0
    AGENT_IDX = 1

    if visualize:
        # game visualizer
        visualizer = GameVisualizer(model_idx=MCTS_IDX)

    

    while not state.is_game_over():

        if visualize:
            visualizer.visualize_state(state)

        # the game cannot be longer than 800 turns, in this case longer snake wins, regardless of the other being alive
        if state.turn > 800:
             if len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MCTS_IDX].tail):
                 return "agent", state
             else:
                 return "MCTS", state

        # agent's snake is longer and llm's is dead, no point of further gameplay
        if len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MCTS_IDX].tail) and (MCTS_IDX in state.eliminated_snakes):
            return "agent", state
        # llm's is longer and agent's is dead
        elif len(state.snakes[MCTS_IDX].tail) > len(state.snakes[AGENT_IDX].tail) and (AGENT_IDX in state.eliminated_snakes):
            return "MCTS", state
            
        # python is snake 1
        snake_moving_idx = state.turn % n_snakes

        if snake_moving_idx == MCTS_IDX:
            direction = agent.mcts_based_agent(state, MCTS_IDX, 30)
  
            # given direction move
            state.move(direction, MCTS_IDX)
          
        else:


            direction = agent.bfs_based_agent(state, AGENT_IDX)

            # given direction move
            state.move(direction, AGENT_IDX)

    
        


if __name__ == "__main__":
    print(main())