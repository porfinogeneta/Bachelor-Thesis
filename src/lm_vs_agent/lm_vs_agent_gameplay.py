
from src.lm_vs_agent.game_visualizer import GameVisualizer
from typing import Tuple

import sys
import os
# visualizer
# from src.snake_game.game_visualizer import GameVisualizer
from src.lm_vs_agent.game_visualizer import GameVisualizer

# llm caller
from src.lm_vs_agent.lm_caller import LLMCaller

from src.lm_vs_agent.utils import create_game_sequence

from src.consts import APPLES_CORPORA, STANDARD, NO_TAILS, MINIMAL

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

def main(model_configuration: Tuple[str, str], sample_valid_tokens: bool, device: str, agent_type: str = "bfs"):
    """
    Runs the snake game simulation using the C++ classes exposed via pybind11 and language model.

    returns the amount of improper generations and string literal llm, agent on game over
    """

    model_name, corpora_type = model_configuration

    parser = argparse.ArgumentParser(description="Run the Snake game simulation.")
    parser.add_argument('-V', '--visualize', action='store_true', help='Enable game visualization')

    args = parser.parse_args()

    visualize = args.visualize

    

    # llm caller
    caller = LLMCaller(model_name=model_name, device=device)

   
   
    # Create instances of the C++ State and Agent classes
    state = snake_lib.State(n_snakes, n_apples, board_width, board_height)
    agent = snake_lib.Agent()

    # MODEL_IDX = random.choice([0, 1])
    # AGENT_IDX = 1 if MODEL_IDX == 0 else 0
    MODEL_IDX = 0
    AGENT_IDX = 1

    # # initialize both snakes
    # game_sequence = "<START> "
    # game_sequence += f"S0 R{state.snakes[0].head[0]}C{state.snakes[0].head[1]} L{len(state.snakes[0].tail)} "
    # game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "
    # game_sequence += f"S1 R{state.snakes[1].head[0]}C{state.snakes[1].head[1]} L{len(state.snakes[1].tail)} "
    # game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "

    # initialize game sequence
    game_sequence = create_game_sequence(corpora_type, "", None, state)

    # counter of improper moves generation of a model
    improper_genenerations_cnt = 0

    # visualize = False

    if visualize:
        # game visualizer
        visualizer = GameVisualizer(model_idx=MODEL_IDX, snake_name="LM")

    

    while not state.is_game_over():

        if visualize:
            visualizer.visualize_state(state)

            
        # python is snake 1
        snake_moving_idx = state.turn % n_snakes

        if snake_moving_idx == MODEL_IDX:

            # snake was eleminated not need for any generation, skip the turn
            if MODEL_IDX in state.eliminated_snakes:
                state.turn += 1
                continue
            
            prev_state = state.deepCopy()
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

            state.move(batch_moves[0], MODEL_IDX)

            game_sequence = create_game_sequence(corpora_type, game_sequence, prev_state, state)
        else:


            # direction = agent.mcts_based_agent(state, AGENT_IDX, 25)
            direction = agent.bfs_based_agent(state, AGENT_IDX)

            # given direction move
            prev_state = state.deepCopy()
            state.move(direction, AGENT_IDX)

            game_sequence = create_game_sequence(corpora_type, game_sequence, prev_state, state)
    
    
    # agent is snake 0
    if len(state.snakes[AGENT_IDX].tail) > len(state.snakes[MODEL_IDX].tail):
        return improper_genenerations_cnt, "agent", state
    else:
        return improper_genenerations_cnt, "model", state
        


if __name__ == "__main__":
    # MODEL_NAME = "mcts_standard_positions/out_mcts_standard_positions_bs_2560"
    MODEL_NAME = "standard_positions/out_standard_positions_bs_4352"
    CORPORA_TYPE = STANDARD
    print(main(model_configuration=(MODEL_NAME, CORPORA_TYPE), sample_valid_tokens=True, device="mps"))