
from src.lm_vs_agent.game_visualizer import GameVisualizer
import subprocess
import os
import re
import random
from typing import Tuple

import sys
import os
# visualizer
# from src.snake_game.game_visualizer import GameVisualizer
from src.lm_vs_agent.game_visualizer import GameVisualizer

# llm caller
from src.lm_vs_agent.lm_caller import LLMCaller

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

def main(model_0_idx: int, model_1_idx: int, model_0_name: str, model_1_name: str, sample_valid_tokens_0: bool, sample_valid_tokens_1: bool, device: str):
    """
    Runs the snake game simulation using the C++ classes exposed via pybind11 and language model.

    returns the amount of improper generations and string literal llm, agent on game over
    """

    parser = argparse.ArgumentParser(description="Run the Snake game simulation.")
    parser.add_argument('-V', '--visualize', action='store_true', help='Enable game visualization')

    args = parser.parse_args()

    visualize = args.visualize

    

    # llm caller
    caller_model_0 = LLMCaller(model_name=model_0_name, device=device)
    caller_model_1 = LLMCaller(model_name=model_1_name, device=device)

    game_sequence = "<START> "
   
    # Create instances of the C++ State and Agent classes
    state = snake_lib.State(n_snakes, n_apples, board_width, board_height)
    state_2 = state.deepCopy()

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
        visualizer = GameVisualizer(model_idx=model_0_idx, snake_name="Context 2220")
        # visualizer_2 = GameVisualizer(model_idx=model_0_idx, snake_name="Sampled Snake")


    def generate_move(sample_valid_tokens: bool, model_idx: int, state: snake_lib, caller: LLMCaller):

        prev_head = state.snakes[model_idx].head

        if sample_valid_tokens:

            batch_moves, ict, cnt = caller.sample_next_batch_moves_from_legal_tokens(
                prev_heads=[prev_head], 
                game_sequences=[f"{game_sequence}S{model_idx}"],
                states=[state],
                language_model_snake_idx=model_idx
            )

        else:
            batch_moves, ict, cnt = caller.sample_next_batch_moves(
                prev_heads=[prev_head], 
                game_sequences=[f"{game_sequence}S{model_idx}"],
                top_k=1
            )
                
        if ict != [None]:
            logger.error(f"model idx: {model_idx} token: {ict} counter: {cnt} turn: {state.turn}")

        return batch_moves, cnt

    

    while not state.is_game_over():

        if visualize:
            visualizer.visualize_state(state)
            # visualizer_2.visualize_state(state_2)

        # the game cannot be longer than 800 turns, in this case longer snake wins, regardless of the other being alive
        if state.turn > 800:
             if len(state.snakes[model_1_idx].tail) > len(state.snakes[model_0_idx].tail):
                 return improper_genenerations_cnt, "model_1", state
             else:
                 return improper_genenerations_cnt, "model_0", state

        # agent's snake is longer and llm's is dead, no point of further gameplay
        if len(state.snakes[model_1_idx].tail) > len(state.snakes[model_0_idx].tail) and (model_0_idx in state.eliminated_snakes):
            return improper_genenerations_cnt, "model_1", state
        # llm's is longer and agent's is dead
        elif len(state.snakes[model_0_idx].tail) > len(state.snakes[model_1_idx].tail) and (model_1_idx in state.eliminated_snakes):
            return improper_genenerations_cnt, "model", state
            
        # python is snake 1
        snake_moving_idx = state.turn % n_snakes

        if snake_moving_idx == model_0_idx:

            # snake was eleminated not need for any generation, skip the turn
            if model_0_idx in state.eliminated_snakes:
                state.turn += 1
                continue

            batch_moves, cnt = generate_move(sample_valid_tokens_0, model_0_idx, state, caller_model_0)
            # batch_moves_2, cnt_2 = generate_move(not sample_valid_tokens_0, model_0_idx, state, caller_model_0)

            # if cnt_2 == 0 and batch_moves[0] != batch_moves_2[0]:
            #     logger.error("jak inne ruch, jak ppb ma być takie samo xd")
            #     logger.error(f"{state.get_game_state()}")
            #     logger.error(game_sequence)
            #     logger.error(f"Batch move no sampling {batch_moves[0]}")
            #     logger.error(f"Batch move sampling {batch_moves_2[0]}")
            #     break
            
            # given direction move, batch_moves is a lists, hence [0]
            state.move(batch_moves[0], model_0_idx)

         
            # add current S_MODEL_IDX position
            game_sequence += f"S{model_0_idx} R{state.snakes[model_0_idx].head[0]}C{state.snakes[model_0_idx].head[1]} L{len(state.snakes[model_0_idx].tail)} "
            game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "

        else:
            # state.turn += 1
            # game_sequence += f"S{model_1_idx} R{state.snakes[model_1_idx].head[0]}C{state.snakes[model_1_idx].head[1]} L{len(state.snakes[model_1_idx].tail)} "
            # game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "
            # continue
            # snake was eleminated not need for any generation, skip the turn
            if model_1_idx in state.eliminated_snakes:
                state.turn += 1
                continue

            batch_moves, _ = generate_move(sample_valid_tokens_1, model_1_idx, state, caller_model_1)
            
            # given direction move, batch_moves is a lists, hence [0]
            state.move(batch_moves[0], model_1_idx)

            # add current S_AGENT_IDX position
            game_sequence += f"S{model_1_idx} R{state.snakes[model_1_idx].head[0]}C{state.snakes[model_1_idx].head[1]} L{len(state.snakes[model_1_idx].tail)} "
            game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "

    
    # agent is snake 0
    if len(state.snakes[model_1_idx].tail) > len(state.snakes[model_0_idx].tail):
        return improper_genenerations_cnt, "agent", state
    else:
        return improper_genenerations_cnt, "model", state
        


if __name__ == "__main__":
    # GAME CONFIGURATION
    # 0 is just a for a model distinction, it doesn't mean the order of play
    #"standard_positions/out_standard_positions_bs_1600"
    MODE_0_IDX = 0
    MODE_1_IDX = 1 - MODE_0_IDX
    MODE_0_NAME = "standard_positions/out_standard_positions_bs_2240"
    MODEL_1_NAME = "standard_positions/out_standard_positions_bs_1600"
    SAMPLE_VALID_TOKENS_0 = False
    SAMPLE_VALID_TOKENS_1 = False
    DEVICE = "mps"

    print(main(model_0_idx=MODE_0_IDX, model_1_idx=MODE_1_IDX,
        model_0_name=MODE_0_NAME, model_1_name=MODEL_1_NAME,
        sample_valid_tokens_0=SAMPLE_VALID_TOKENS_0,
        sample_valid_tokens_1=SAMPLE_VALID_TOKENS_1,
        device=DEVICE
        ))

    # print(main(model_0_idx=0, model_1_idx=1 model_name="aligned_games/out_aligned_bs_4352", sample_valid_tokens_0=True, sample_valid_tokens_1=False, device="mps"))