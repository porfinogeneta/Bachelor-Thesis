from typing import List
import pygame
import random

from game_config import GameConfig
from apple import Apple
from snake import Snake


class Game:
    def __init__(self, config):
        self.snake = Snake(start_pos=(8, 8), config=config)
        self.config = config
        self.apples = [Apple(self.snake.body, config=config) for _ in range(config.APPLES_AMOUNT)]

        self.apple_surface = pygame.Surface((config.cell_size, config.cell_size))
        self.apple_surface.fill(config.APPLE)

    def draw(self):
        self.config.screen.fill(self.config.DARK_GREEN)
        self.snake.draw()
        self.draw_apples()


    def handle_input_direction(self, prompt: str = "enter direction") -> tuple[int, int]:
        # MU - move up
        allowed_inputs = ["MU", ",MD", "ML", "MR"]


        tuple_map = {
            "MU": (0, -1),
            "MD": (0, 1),
            "ML": (-1, 0),
            "MR": (1, 0)
        }

        inp = input(prompt).strip().upper()

        if inp not in allowed_inputs:
            inp = random.choice(allowed_inputs)
            return tuple_map[inp]

        return tuple_map[inp]

    def draw_apples(self):
       for apple in self.apples:
            x, y = apple.position
            self.config.screen.blit(self.apple_surface, 
                                  (x * self.config.cell_size, 
                                   y * self.config.cell_size))


    def is_colliding_with_apple(self, snake: Snake) -> bool:
        is_colliding = False
        for i, apple in enumerate(self.apples):
            if apple.position == snake.body[0]:
                self.apples[i] = Apple(snake.body, self.config)    
                is_colliding = True
                snake.score += 1
        
        return is_colliding
    
    def is_colliding_with_wall(self, snake: Snake, direction: tuple[int, int]) -> bool:
        head_x, head_y = (snake.body[0][0] + direction[0], snake.body[0][1] + direction[1])
        # print(head_x, head_y)
        return head_x < 0 \
            or head_x > self.config.width // self.config.cell_size \
            or head_y < 0 \
            or head_y > self.config.height // self.config.cell_size
            
    def is_colliding_snake_with_self(self, snake: Snake, direction: tuple[int, int]):
        head = (snake.body[0][0] + direction[0], snake.body[0][1] + direction[1])
        return head in snake.body[1:]

    def game_over(self, snake: Snake):
        print(snake.score)
        snake.reset()


    def run(self):
        running = True
        direction = (0, 0)
        while running:

            # direction = self.handle_input_direction()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        direction = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        direction = (0, 1)
                    elif event.key == pygame.K_LEFT:
                        direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        direction = (1, 0)

            
            ate_apple = self.is_colliding_with_apple(snake=self.snake)
            # there is a side case when snake_len = 2 then we need to check if the updated direction will cause collision
            # in other cases it's not necessary
            if self.is_colliding_with_wall(self.snake, direction) or self.is_colliding_snake_with_self(self.snake, direction):
                self.game_over(self.snake)
            
            self.snake.update(direction, ate_apple=ate_apple)

            self.draw()


            pygame.display.flip()
            self.config.clock.tick(self.config.fps)

        pygame.quit()

if __name__ == "__main__":
    config = GameConfig()
    game = Game(config)
    game.run()