from typing import List
import pygame

from game_config import GameConfig

class Snake:
    def __init__(self, x: int, y: int):
       self.head = (x, y)
       self.tail = []
       self.moves_history = []


    def get_move(self, direction: str):
       if direction == "U":
          return (-1, 0)
       elif direction == "D":
          return (1, 0)
       elif direction == "L":
          return (0, -1)
       elif direction == "R":
          return (0, 1)
       else:
          return (0, 0)
       
    def move(self, direction: str):
       move = self.get_move(direction)
       head_cpy = self.head
       self.head = (self.head[0] + move[0], self.head[1] + move[1])
       
       if len(self.tail) > 0:
         self.tail.pop()
         self.tail.insert(0, head_cpy)

    def get_last_snake_segment(self):
         if len(self.tail) > 0:
          return self.tail[-1]
         else:
          return self.head


    