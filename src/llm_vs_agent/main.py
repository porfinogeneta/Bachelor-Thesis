import socket
import threading
import json
import time
from src.snake_game.serializer import Serializer
from src.snake_game.game_visualizer import GameVisualizer
import subprocess
import os
import re
import logging
import random

import logging
from src.logger.logger import setup_logger

logger = setup_logger(__name__)


# leftover_data = ""
def receive_complete_json(sock):
    buffer = ""
    depth = 0
    in_json = False
    beginning = 0
    # global leftover_data
    # buffer = leftover_data
    # leftover_data = ""
    
    while True:
        chunk = sock.recv(1024).decode('utf-8')
        if chunk == "":
            return None

        buffer += chunk

        if chunk == "":
            return None

        for i, s in enumerate(buffer):
            if s == "{":
                if depth == 0:
                    in_json = True
                    beginning = i
                depth += 1
            elif s == "}":
                depth -= 1
                if depth == 0 and in_json:
                    result = buffer[beginning:i+1]
                    # leftover_data = buffer[i+1:]
                    return result
        
       
def is_move_valid(prev_head: tuple[int, int], current_head: tuple[int, int]):
    # up
    if (prev_head[0] - 1, prev_head[1]) == current_head:
        return True
    # down
    elif (prev_head[0] + 1, prev_head[1]) == current_head:
        return True
    # left
    elif (prev_head[0], prev_head[1] - 1) == current_head:
        return True
    # right
    elif (prev_head[0], prev_head[1] + 1) == current_head:
        return True
    else: return False


def select_majority_elem(lst):
    return max(set(lst), key=lst.count)


def run_lm(prev_head: tuple[int, int], model: str, game_sequence: str, max_new_tokens: int, n_samples: int):

    nanoGPT_dir = "/Users/szymon/Documents/Bachelor-Thesis/src/training/nanoGPT"

    


    os.chdir(nanoGPT_dir)
    result = subprocess.run(['python3', 'sample.py', f'--out_dir={model}',
                        '--device=mps', f'--start={game_sequence}',
                        f'--max_new_tokens={max_new_tokens}', f'--num_samples={n_samples}'], capture_output=True, text=True)

    generated_sequences = result.stdout.split("---------------")[1:]

    if not generated_sequences:
        raise Exception("Unable to generate :(") 
    
    valid_moves = []

    for seq in generated_sequences:
        # logger.info(seq)
        # print(seq[len(game_sequence)+1:])
        generated_position = seq[len(game_sequence)+1:]

        # logger.info(generated_position)

        pattern = r"\d+"
        current_head = tuple([int(elem) for elem in re.findall(pattern, generated_position)])

        # print(current_head)
        if is_move_valid(prev_head, current_head):
            valid_moves.append(current_head) 

    if not valid_moves:
        raise Exception("Model don't understand valid moves :(")

    return random.choice(valid_moves) 

def get_direction_based_on_heads(prev_head: tuple[int, int], current_head: tuple[int, int]) -> str:
    # up
    if (prev_head[0] - 1, prev_head[1]) == current_head:
        return "W"
    # down
    elif (prev_head[0] + 1, prev_head[1]) == current_head:
        return "S"
    # left
    elif (prev_head[0], prev_head[1] - 1) == current_head:
        return "A"
    # right
    elif (prev_head[0], prev_head[1] + 1) == current_head:
        return "D"


#iter 10000: loss 0.7874, time 1995.32ms, mfu 0.11%
if __name__ == "__main__":

    game_sequence = "<START> "
    
    # print(run_lm(prev_head=(6,3), model="out-standard_pos", game_sequence="<START> S0 R5C1 L0 A99 A15 A69 A52 A18 S1 R7C3 L0 A99 A15 A69 A52 A18 S0 R5C2 L1 A99 A15 A69 A18 A28 S1 R6C3 L0 A99 A15 A69 A18 A28 S0 R4C2 L1 A99 A15 A69 A18 A28 S1",
    #        max_new_tokens=4, n_samples=10))
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 8080)

    print("Python client connecting to C++ server...")
    client_socket.connect(server_address)
    print("Connected to C++ server!")


    # C++ server begins a game by sending a state either after it's move
    # or just the initial state, so at the beginning it's cpp turn
    is_python_turn = False

    # game visualizer
    visualizer = GameVisualizer()
    
    while True:

        
        if is_python_turn:
            if state.is_game_over():
                print("Python won")
                break
            
            print("Python's turn...")            
            
            # # Make move and update state
            # direction = input("provide move: ").upper()

            # get previous python snake head's position
            prev_head = state.snakes[1].head

            try:
                direction = get_direction_based_on_heads(prev_head, run_lm(prev_head=prev_head, model="out-standard_pos", game_sequence=f"{game_sequence}S1", max_new_tokens=1, n_samples=20))
            except Exception as e:
                logger.error(e)
                direction = "W" # probabilistically best move xd

            
            state.move(direction=direction, snake_moving_idx=1)

            # visualize
            visualizer.visualize_state(state)
            
            # Send updated state back to C++ server
            serialized_state = Serializer.serialize_state(state)
            print("Sending:", serialized_state)
            client_socket.sendall(serialized_state.encode('utf-8'))
            is_python_turn = False

            game_sequence += f"S1 R{state.snakes[1].head[0]}C{state.snakes[1].head[1]} L{len(state.snakes[1].tail)} "
            game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "
            

            print(game_sequence)

            # After python move snake is dead, means cpp won
            if state.is_game_over():
                print("C++ won")
                break

        else:
            print("C++'s turn...")
            # Receive game state from C++ server
            serialized_state = receive_complete_json(client_socket)
            if not serialized_state:
                continue

            # Parse received state
            state = Serializer.deserialize_state(serialized_state)

            # visualize
            visualizer.visualize_state(state)

            

            # set up initial positions of both snakes
            if state.turn == 1:
                game_sequence += f"S0 R{state.snakes[0].moves_history[0][0]}C{state.snakes[0].moves_history[0][1]} L{len(state.snakes[0].tail)} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "
                game_sequence += f"S1 R{state.snakes[1].head[0]}C{state.snakes[1].head[1]} L{len(state.snakes[1].tail)} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "

            # add current S0 position
            game_sequence += f"S0 R{state.snakes[0].head[0]}C{state.snakes[0].head[1]} L{len(state.snakes[0].tail)} "
            game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in state.apples]) + " "

            print(f"Received: {serialized_state}")
            is_python_turn = True

            print(game_sequence)

            # After cpp move game is over, means python won
            if state.is_game_over():
                print("Python won")
                break
    
    client_socket.close()
    visualizer.close()
    print("Game over!")

