from typing import List
from snake import Snake
from apple import Apple
import json

class State:
    def __init__(self, n_snakes: int, n_apples: int, board_width: int, board_height: int):
        self.n_snakes = n_snakes
        self.n_apples = n_apples
        self.board_width = board_width
        self.board_height = board_height


        self.snakes = []
        self.apples = []
        self.eliminated_snakes = set()
        self.turn = 0
        self.idx_prev_snake = None
        self.whoose_prev_turn = ""

    def is_snake_colliding_snakes(self, snake: Snake, snakes: List[Snake]) -> bool:
        moving_head = snake.head

        if moving_head in snake.tail:
            return True
        
        for other_snake in snakes:
            if other_snake == snake:
                continue

            if moving_head == other_snake.head:
                return True

            if moving_head in other_snake.tail:
                return True
            
        return False
    
    def is_snake_out_of_bounds(self, snake: Snake) -> bool:
        head_x, head_y = snake.head
        return head_x < 0 \
            or head_x > self.board_width - 1 \
            or head_y < 0 \
            or head_y > self.board_height - 1
    

    def is_snake_colliding_with_apple(self, snake: Snake, apples: List[Apple]) -> bool:
        moving_head = snake.head
        for i, apple in enumerate(apples):
            if apple.position == moving_head:
                apples.pop(i)
                return True
        return False
    

    def move(self, direction: str, snake_moving_idx: int):
        """
            Returns False if the move is not possible
        """
        self.idx_prev_snake = snake_moving_idx
        if (snake_moving_idx in self.eliminated_snakes):
            return False
        
        new_snake_segment = self.snakes[snake_moving_idx].get_last_snake_segment()

        self.snakes[snake_moving_idx].move(direction)
        self.snakes[snake_moving_idx].moves_history.append(self.snakes[snake_moving_idx].head)

        if self.is_snake_colliding_snakes(self.snakes[snake_moving_idx], self.snakes) \
            or self.is_snake_out_of_bounds(self.snakes[snake_moving_idx]):
                
                self.eliminated_snakes.add(snake_moving_idx)
                return False
        

        if self.is_snake_colliding_with_apple(self.snakes[snake_moving_idx], self.apples):
            self.snakes[snake_moving_idx].tail.append(new_snake_segment)


        return True
    
    def is_game_over(self) -> bool:
        return len(self.eliminated_snakes) == self.n_snakes
    
   
    