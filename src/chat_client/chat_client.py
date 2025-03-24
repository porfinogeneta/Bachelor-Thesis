import socket
import json
import time
import random

class ChatClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.possible_moves = ["up", "down", "left", "right"]
        self.game_state = None

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print(f"Connected to game server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
        
    
    def receive_game_state(self):
        try:
            data = self.socket.recv(1024).decode()
            if data:
                self.game_state = json.loads(data)
                print(f"Received game state: {self.game_state}")
                return self.game_state
            return None
        except Exception as e:
            print(f"Error receiving game state: {e}")
            return None
        
    def send_move(self, move):
        try:
            move_data = json.dumps({"action": move})
            self.socket.send(move_data.encode())
            print(f"Sent move: {move}")
            return True
        except Exception as e:
            print(f"Error sending move: {e}")
            return False
        
    def decide_move(self):
        return random.choice(self.possible_moves)
    
    def play_game(self):
        if not self.connect():
            return
        
        self.receive_game_state()

    
if __name__ == "__main__":
    client = ChatClient()
    client.play_game()