
from src.lm_vs_agent.game_visualizer import GameVisualizer
import time
import sys
# visualizer
# from src.snake_game.game_visualizer import GameVisualizer
from src.lm_vs_agent.game_visualizer import GameVisualizer
from src.consts import N_SNAKES, N_APPLES, BOARD_WIDTH, BOARD_HEIGHT

# logger
from src.logger.logger import setup_logger

logger = setup_logger(__name__)


from src.consts import PYBIND_DIR

sys.path.append(str(PYBIND_DIR))

import snake_lib

import argparse
import sys


# # Game configurations
# n_snakes = 2
# n_apples = 5
# board_width = 10
# board_height = 10

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
    state = snake_lib.State(N_SNAKES, N_APPLES, BOARD_WIDTH, BOARD_HEIGHT)
    agent = snake_lib.Agent()

    # MCTS_IDX = random.choice([0, 1])
    # AGENT_IDX = 1 if MODEL_IDX == 0 else 0
    MCTS_IDX = 0
    AGENT_IDX = 1

    if visualize:
        # game visualizer
        visualizer = GameVisualizer(model_idx=MCTS_IDX, snake_name="Minimax")

    # time.sleep(5)

    while not state.is_game_over():

        if visualize:
            visualizer.visualize_state(state)
        
            
        # python is snake 1
        snake_moving_idx = state.turn % N_SNAKES

        if snake_moving_idx == MCTS_IDX:
            direction = agent.minimax_based_agent(state, MCTS_IDX, 8)
            # direction = agent.mcts_based_agent(state, MCTS_IDX, 25)
  
            # given direction move
            state.move(direction, MCTS_IDX)
          
        else:

            # direction = agent.mcts_based_agent(state, AGENT_IDX, 25)
            direction = agent.bfs_based_agent(state, AGENT_IDX)

            # given direction move
            state.move(direction, AGENT_IDX)


    winner = state.get_winner()
    if winner == AGENT_IDX:
        return "agent", state
    elif winner == MCTS_IDX:
        return "MCTS", state
    else:
        return "tie", state

    
    

if __name__ == "__main__":
    print(main())