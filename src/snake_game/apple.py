import random
from typing import List
import pygame
from game_config import  GameConfig

class Apple:
    def __init__(self, snake_segmens_locations: List[tuple[int, int]], config: GameConfig):
        self.config = config
        self.position = self.generate_random_pos(snake_segmens_locations)

    def generate_random_pos(self, snake_segmens_locations: List[tuple[int, int]]):
        """
            Generate apple in random square pos, we allow multiple apples to be in the same location,
            LLM should aim for this kind of apples then…
        """
        snake_segmens_locations = set(snake_segmens_locations)
        x = random.randint(0, self.config.width // self.config.cell_size - 1)
        y = random.randint(0, self.config.height // self.config.cell_size- 1)

        while ((x, y) in snake_segmens_locations):
            x = random.randint(0, self.config.width // self.config.cell_size - 1)
            y = random.randint(0, self.config.height // self.config.cell_size - 1)

        return (x, y)
    
    def draw(self):
        x, y = self.position
        apple_rect = (x * self.config.cell_size,
                       y * self.config.cell_size,
                       self.config.cell_size,
                       self.config.cell_size)
        pygame.draw.rect(self.config.screen, self.config.APPLE, apple_rect)
