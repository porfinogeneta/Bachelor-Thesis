import pygame

class Apple:
    def __init__(self, x: int, y: int):
        self.position = (x, y)

    
    
    def draw(self):
        x, y = self.position
        apple_rect = (x * self.config.cell_size,
                       y * self.config.cell_size,
                       self.config.cell_size,
                       self.config.cell_size)
        pygame.draw.rect(self.config.screen, self.config.APPLE, apple_rect)
