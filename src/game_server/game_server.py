import socket
import json
import threading
import time

# local packages
from snake_game_client.main import Game
from snake_game_client.game_config import GameConfig


class GameServer:
    def __init__(self, host="localhost", port=5000):
        self.host = host
        self.port = port
        self.game = Game(GameConfig())
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True

    def accept_clients(self):
        while self.running:
            try:
                client_socket, addr = self.socket.accept()
                print(f"Connected to chatbot client: {addr}")
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                print(f"Error accepting client: {e}")
                if not self.running:
                    break


    def handle_client(self, client_socket):
        try:
            initial_state = json.dump({"some random dict": 1})
            client_socket.send(initial_state.encode())

            while self.running and not self.game.is_game_over:
                data = client_socket.recv(1024).decode()
                if not data:
                    break

                move = json.loads(data)
                print(f"Received move from chatbot: {move}")
                
                new_state = self.game_state.update(move["action"])
                
                client_socket.send(json.dumps(new_state).encode())
                
                time.sleep(0.2)

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def start(self):
        self.socket.bind(self.host, self.port)
        self.socket.listen(1)
        print(f"Game server listening on {self.host}:{self.port}")

        threading.Thread(target=self.ac)

        self.game.run()



if __name__ == "__main__":
    server = GameServer()
    server.start()