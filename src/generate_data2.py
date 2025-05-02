import sys
import os


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

def main():
    """
    Runs the snake game simulation using the C++ classes exposed via pybind11.
    """
    parser = argparse.ArgumentParser(description="Run the Snake game simulation.")
    parser.add_argument('-V', '--verbose', action='store_true', help='Enable verbose output (print game state each turn).')
    parser.add_argument('-H', '--history', action='store_true', help='Provide full game history at the end.')
   
    args = parser.parse_args()

    verbose = args.verbose
    provide_history = args.history

    # Create instances of the C++ State and Agent classes
    state = snake_lib.State(n_snakes, n_apples, board_width, board_height)
    agent = snake_lib.Agent()


    while not state.is_game_over():
        if verbose:
            print(f"\n--- Turn {state.turn} ---")
            state.print_game_state()

        snake_moving_idx = state.turn % n_snakes

        # In Python, we don't need to check state.eliminated_snakes here
        # because the C++ State::move method should handle if a snake is eliminated
        # and prevent it from moving.

        # Get the move direction from the BFS-based agent
        direction = agent.bfs_based_agent(state, snake_moving_idx)
        # print(f"Snake {snake_moving_idx} moving: {direction}")

        # Move the snake in the State
        state.move(direction, snake_moving_idx)

    # Game is over
    
    if verbose:
        print("\n--- Game Over ---")
        state.print_game_state()

    if provide_history:
        print("\n--- Game History ---")
        state.get_full_history()

if __name__ == "__main__":
    main()