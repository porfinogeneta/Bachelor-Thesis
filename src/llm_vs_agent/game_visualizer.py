




import pygame
import sys
import json
# from serializer import Serializer  # Using your existing serializer

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Snake colors - we'll use different colors for different snakes
SNAKE_COLORS = [
    (50, 205, 50),   # Snake 0: Lime Green
    (0, 191, 255),   # Snake 1: Deep Sky Blue
    (255, 69, 0),    # Snake 2: Orange Red
    (138, 43, 226),  # Snake 3: Blue Violet
    (255, 215, 0),   # Snake 4: Gold
]

class GameVisualizer:
    def __init__(self, model_idx, board_width=10, board_height=10, cell_size=40):
        self.model_idx = model_idx
        self.board_width = board_width
        self.board_height = board_height
        self.cell_size = cell_size
        
        # Initialize pygame
        pygame.init()
        self.font = pygame.font.SysFont('Arial', 18)
        
        # Calculate window size
        self.window_width = board_width * cell_size
        self.window_height = board_height * cell_size
        
        # Create the window
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Snake Game Visualization")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
    
    def update_dimensions(self, width, height):
        """Update board dimensions if they change"""
        if width != self.board_width or height != self.board_height:
            self.board_width = width
            self.board_height = height
            self.window_width = width * self.cell_size
            self.window_height = height * self.cell_size
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
    
    def draw_grid(self):
        """Draw the grid lines"""
        for x in range(0, self.window_width, self.cell_size):
            pygame.draw.line(self.screen, BLACK, (x, 0), (x, self.window_height))
        for y in range(0, self.window_height, self.cell_size):
            pygame.draw.line(self.screen, BLACK, (0, y), (self.window_width, y))
    
    def draw_apple(self, pos):
        """Draw an apple at the given position where pos = [row, col]"""
        row, col = pos
        # Convert row, col to x, y coordinates for drawing
        x = col * self.cell_size
        y = row * self.cell_size
        
        rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, RED, rect)
        
        # Draw a small stem
        stem_rect = pygame.Rect(
            x + self.cell_size // 2 - 2, 
            y - 3, 
            4, 
            6
        )
        pygame.draw.rect(self.screen, GREEN, stem_rect)
    
    def draw_snake(self, snake, color):
        """Draw a snake with its head and tail using row-column coordinates"""
        # Draw head
        head_row, head_col = snake.head
        # Convert to pixel coordinates
        head_x = head_col * self.cell_size
        head_y = head_row * self.cell_size
        
        head_rect = pygame.Rect(head_x, head_y, self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, color, head_rect)
        
        # Draw eyes on head
        eye_size = self.cell_size // 8
        eye1_pos = (head_x + self.cell_size // 3, head_y + self.cell_size // 3)
        eye2_pos = (head_x + 2 * self.cell_size // 3, head_y + self.cell_size // 3)
        pygame.draw.circle(self.screen, BLACK, eye1_pos, eye_size)
        pygame.draw.circle(self.screen, BLACK, eye2_pos, eye_size)
        
        # Draw tail segments
        for segment in snake.tail:
            tail_row, tail_col = segment
            # Convert to pixel coordinates
            tail_x = tail_col * self.cell_size
            tail_y = tail_row * self.cell_size
            
            tail_rect = pygame.Rect(tail_x, tail_y, self.cell_size, self.cell_size)
            # Make tail slightly darker than head
            darker_color = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40))
            pygame.draw.rect(self.screen, darker_color, tail_rect)
    
    def draw_eliminated_info(self, eliminated_snakes):
        """Draw info about eliminated snakes"""
        if eliminated_snakes:
            eliminated_text = f"Eliminated: {', '.join(map(str, eliminated_snakes))}"
            text_surface = self.font.render(eliminated_text, True, BLACK)
            self.screen.blit(text_surface, (10, 10))
    
    def draw_turn_info(self, turn, prev_turn):
        """Draw turn information"""
        turn_text = f"Turn: {turn}\nModel index: {self.model_idx}"
        text_surface = self.font.render(turn_text, True, BLACK)
        self.screen.blit(text_surface, (10, 30))

    def visualize_state(self, state):
        """Visualize the current game state"""
        # Handle pygame events to keep window responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Update dimensions if needed
        self.update_dimensions(state.board_width, state.board_height)
        
        # Clear screen
        self.screen.fill(WHITE)
        
        # Draw grid
        self.draw_grid()
        
        
        # Draw apples
        for apple_obj in state.apples:
            self.draw_apple(apple_obj.position)
        
        # Draw snakes
        for i, snake in enumerate(state.snakes):
            if i == self.model_idx:
                self.draw_snake(snake, BLUE)
            else:
                 self.draw_snake(snake, GREEN)
                 
        # Draw information
        self.draw_eliminated_info(state.eliminated_snakes)
        self.draw_turn_info(state.turn, state.whoose_prev_turn)
        
        # Update display
        pygame.display.flip()
        self.clock.tick(5)  # 5 FPS is good for visualization
    
    def close(self):
        """Close the visualization"""
        pygame.quit()


# # Add this to your main loop
# def main():
#     # Sample state for testing
#     sample_state_json = """{"n_snakes": 2, "n_apples": 5, "board_width": 10, "board_height": 10, "turn": 4, "snakes": [{"id": 0, "head": [4, 10], "tail": [[4, 9]], "moves_history": [[4, 7], [4, 8], [4, 9], [4, 10]]}, {"id": 1, "head": [5, 4], "tail": [], "moves_history": [[6, 7], [6, 6], [5, 6], [5, 5], [5, 4]]}], "apples": [[5, 1], [5, 3], [4, 4], [1, 2], [3, 2]], "eliminated_snakes": [0], "idx_prev_snake": 0, "whoose_prev_turn": "py"}"""
#     sample_state = Serializer.deserialize_state(sample_state_json)
    
#     visualizer = GameVisualizer()
#     visualizer.visualize_state(sample_state)
    
#     # Just for testing - keep window open
#     running = True
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
    
#     visualizer.close()

# # If running this file directly, show a test visualization
# if __name__ == "__main__":
#     main()


# To integrate with your existing socket code:
"""
# Add at the top your original file:
from game_visualizer import GameVisualizer

# Initialize the visualizer in your main function
visualizer = GameVisualizer()

# Then in your main loop, after receiving or updating state:
visualizer.visualize_state(state)

# At the end of your program:
visualizer.close()
"""