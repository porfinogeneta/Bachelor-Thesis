import pygame


class GameConfig:

    # width and height are in blocks
    def __init__(self, width=10, height=10, fps=10, cell_size=32):

        pygame.init()
    
        self.width = width
        self.height = height
        self.fps = fps
        self.cell_size = cell_size

        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("LLM Snake Game")

        self.cell_size = 32

        self.GREEN = (173, 204, 96)
        self.DARK_GREEN = (43, 51, 24)
        self.APPLE = (150, 0, 0)
        self.APPLES_AMOUNT = 4

