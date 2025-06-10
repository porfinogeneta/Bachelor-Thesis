import sys
import os
from tqdm import tqdm
import multiprocessing

from src.consts import PYBIND_DIR, RAW_DATA_20K, RAW_DATA_TAILS_20K, RAW_DATA_TAILS_MCTS_20K

# cpp code
module_path = '/Users/szymon/Documents/Bachelor-Thesis/python_cpp_binding/'
# module_path = "/home/ubuntu/Bachelor-Thesis/python_cpp_binding/"

# setup logger
from src.logger.logger import setup_logger
logger = setup_logger(__name__)

sys.path.append(module_path)

import argparse
import sys

# Game configurations
n_snakes = 2
n_apples = 5
board_width = 10
board_height = 10


def _play_one_game_task(dummy_arg):

    from src.consts import PYBIND_DIR
    sys.path.append(str(PYBIND_DIR))
    import snake_lib

    # Create instances of the C++ State and Agent classes
    state = snake_lib.State(n_snakes, n_apples, board_width, board_height)
    agent = snake_lib.Agent()


    while not state.is_game_over():
       
        snake_moving_idx = state.turn % n_snakes

        direction = agent.mcts_based_agent(state, snake_moving_idx, 25)

        state.move(direction, snake_moving_idx)

    return state.get_full_history()
        


class DataGenerator:



    def create_data(self, samples: int, output: str):
        results_from_pool = []
        
        # Determine the number of processes to use. Default is os.cpu_count().
        with multiprocessing.Pool() as pool:
            game_results_iterator = pool.imap_unordered(_play_one_game_task, range(samples))
            
            logger.info(f"Running {samples} games in parallel...")
            for result in tqdm(game_results_iterator, total=samples, desc="Tournament Progress"):
                # results_from_pool.append(result)
                with open(output, "a") as file:
                    file.write(result + "\n")
                
            

   


if __name__ == "__main__":
    generator = DataGenerator()

    generator.create_data(20000, RAW_DATA_TAILS_MCTS_20K)

