import socket
import threading
import json
import time
from src.snake_game.serializer import Serializer
from src.snake_game.game_visualizer import GameVisualizer

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
        
       


if __name__ == "__main__":
    

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
            
            # Make move and update state
            direction = input("provide move: ").upper()
            state.move(direction=direction, snake_moving_idx=1)

            # visualize
            visualizer.visualize_state(state)
            
            # Send updated state back to C++ server
            serialized_state = Serializer.serialize_state(state)
            print("Sending:", serialized_state)
            client_socket.sendall(serialized_state.encode('utf-8'))
            is_python_turn = False

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
                
            print(f"Received: {serialized_state}")
            is_python_turn = True

            # After cpp move game is over, means python won
            if state.is_game_over():
                print("Python won")
                break
    
    client_socket.close()
    visualizer.close()
    print("Game over!")