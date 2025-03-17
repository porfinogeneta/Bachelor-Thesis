from typing import List
import pygame

from game_config import GameConfig

class Snake:
    def __init__(self, start_pos: tuple[int, int], config: GameConfig):
        
        # start pos in squares
        self.start_pos_x, self.start_pos_y = start_pos
        self.body = [(self.start_pos_x, self.start_pos_y)]
        self.config = config
        self.color = self.config.GREEN
        self.score = 1
    
    def draw(self):
       for i, pos in enumerate(self.body):
        x, y = pos
        segment_rect = (x * self.config.cell_size,
                       y * self.config.cell_size,
                       self.config.cell_size,
                       self.config.cell_size)
        if i == 0:
            pygame.draw.rect(self.config.screen, (0, 0, 255), segment_rect)
        else:
            pygame.draw.rect(self.config.screen, self.color, segment_rect)

    def update(self, direction: tuple, ate_apple: bool):
        if len(self.body) == 2:
            if (self.body[0][0] + direction[0], self.body[0][1] + direction[1]) == self.body[1]:
                print("hje")
        new_head = (self.body[0][0] + direction[0], self.body[0][1] + direction[1])
        
        self.body.insert(0, new_head)
        if not ate_apple:
            self.body = self.body[:-1]
    
       
    def reset(self):
        self.body = [(self.start_pos_x, self.start_pos_y)]