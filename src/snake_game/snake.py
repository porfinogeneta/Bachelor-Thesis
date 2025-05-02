from typing import List, Tuple
import pygame

from .game_config import GameConfig

class Snake:
    def __init__(self, x: int, y: int):
       self.head: Tuple[int, int] = (x, y)
       self.tail: List[Tuple[int, int]] = []
       self.moves_history: List[Tuple[int, int]]  = []


    def get_move(self, direction: str):
       if direction == "W":
          return (-1, 0)
       elif direction == "S":
          return (1, 0)
       elif direction == "A":
          return (0, -1)
       elif direction == "D":
          return (0, 1)
       else:
          return (0, 0)
       
    def move(self, direction: str):
       move = self.get_move(direction)
      #  if move == (0,0):
      #     return
       head_cpy = self.head
       self.head = (self.head[0] + move[0], self.head[1] + move[1])

       # if snake collides with it
       
       if len(self.tail) > 0:
         self.tail.pop()
         self.tail.insert(0, head_cpy)

    def get_last_snake_segment(self):
         if len(self.tail) > 0:
          return self.tail[-1]
         else:
          return self.head


    