import pygame
import sys
import json
# from serializer import Serializer # Using your existing serializer

# --- New UI Color Palette ---
COLOR_BOARD_LIGHT = (220, 220, 220)  # Light gray for checkerboard
COLOR_BOARD_DARK = (200, 200, 200)   # Darker gray for checkerboard
COLOR_GRID_LINES = (180, 180, 180)  # Subtle grid lines
COLOR_APPLE_BODY = (220, 20, 60)     # Crimson red for apple
COLOR_APPLE_LEAF = (34, 139, 34)     # Forest green for apple leaf/stem
COLOR_SNAKE_EYE = (255, 255, 255)    # White for snake eyes
COLOR_SNAKE_PUPIL = (0, 0, 0)        # Black for snake pupils
COLOR_PANEL_BG = (60, 70, 80)        # Dark slate gray/blue for panel
COLOR_PANEL_TEXT = (230, 230, 230)   # Light gray/off-white for panel text
COLOR_MODEL_SNAKE_HIGHLIGHT = (255, 255, 0) # Yellow to highlight model snake text

# Original Colors (some might be reused or kept for reference)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0) # Original apple color, now using COLOR_APPLE_BODY
RED = (255, 0, 0)   # Original apple color, now using COLOR_APPLE_BODY
BLUE = (0, 0, 255)  # Original model snake color, now using SNAKE_COLORS
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Snake colors - we'll use different colors for different snakes
SNAKE_COLORS = [
    (50, 205, 50),   # Snake 0: Lime Green
    (0, 191, 255),   # Snake 1: Deep Sky Blue
    (255, 69, 0),    # Snake 2: Orange Red
    (138, 43, 226),  # Snake 3: Blue Violet
    (255, 215, 0),   # Snake 4: Gold (Yellowish)
    (255, 105, 180), # Snake 5: Hot Pink
    (0, 255, 255),   # Snake 6: Cyan
]

# --- UI Constants ---
PANEL_WIDTH = 250  # Width of the side information panel
CELL_BORDER_RADIUS_RATIO = 0.2 # For rounded snake segments if using rects, not used for circles
APPLE_RADIUS_RATIO = 0.35      # Apple body radius relative to cell size
APPLE_LEAF_RADIUS_RATIO = 0.1  # Apple leaf radius relative to cell size
SNAKE_SEGMENT_RADIUS_RATIO = 0.45 # Snake segment radius relative to cell size
SNAKE_HEAD_EYE_RADIUS_RATIO = 0.1 # Snake eye radius relative to cell size
SNAKE_HEAD_PUPIL_RADIUS_RATIO = 0.05 # Snake pupil radius relative to cell size


class GameVisualizer:
    def __init__(self, model_idx, board_width=10, board_height=10, cell_size=50): # Reduced cell_size for better fit
        self.model_idx = model_idx
        self.board_width = board_width
        self.board_height = board_height
        self.cell_size = cell_size
        
        pygame.init()
        self.font_panel_header = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_panel_text = pygame.font.SysFont('Arial', 18)
        self.font_model_snake = pygame.font.SysFont('Arial', 18, bold=True)

        self.game_board_width = board_width * cell_size
        self.game_board_height = board_height * cell_size
        
        self.window_width = self.game_board_width + PANEL_WIDTH
        self.window_height = self.game_board_height
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Snake AI Battle Visualization")
        
        self.clock = pygame.time.Clock()
    
    def update_dimensions(self, width, height):
        if width != self.board_width or height != self.board_height:
            self.board_width = width
            self.board_height = height
            
            self.game_board_width = width * self.cell_size
            self.game_board_height = height * self.cell_size
            
            self.window_width = self.game_board_width + PANEL_WIDTH
            # Ensure window height is at least a minimum to accommodate panel text if board is too small
            self.window_height = max(self.game_board_height, 300) # Minimum height for panel
            
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
    
    def draw_grid(self):
        for r in range(self.board_height):
            for c in range(self.board_width):
                rect = pygame.Rect(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
                if (r + c) % 2 == 0:
                    pygame.draw.rect(self.screen, COLOR_BOARD_LIGHT, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_BOARD_DARK, rect)
                pygame.draw.rect(self.screen, COLOR_GRID_LINES, rect, 1) # Grid outline
    
    def draw_apple(self, pos):
        row, col = pos
        center_x = col * self.cell_size + self.cell_size // 2
        center_y = row * self.cell_size + self.cell_size // 2
        
        # Apple body
        radius = int(self.cell_size * APPLE_RADIUS_RATIO)
        pygame.draw.circle(self.screen, COLOR_APPLE_BODY, (center_x, center_y), radius)
        
        # Apple leaf/stem (small circle on top)
        leaf_radius = int(self.cell_size * APPLE_LEAF_RADIUS_RATIO)
        pygame.draw.circle(self.screen, COLOR_APPLE_LEAF, (center_x + radius // 2, center_y - radius // 2), leaf_radius)

    def get_snake_color(self, snake_idx):
        return SNAKE_COLORS[snake_idx % len(SNAKE_COLORS)]

    def draw_snake(self, snake, snake_idx):
        color = self.get_snake_color(snake_idx)
        segment_radius = int(self.cell_size * SNAKE_SEGMENT_RADIUS_RATIO)

        # Draw head
        head_row, head_col = snake.head
        head_center_x = head_col * self.cell_size + self.cell_size // 2
        head_center_y = head_row * self.cell_size + self.cell_size // 2
        
        pygame.draw.circle(self.screen, color, (head_center_x, head_center_y), segment_radius)
        
        # Draw eyes on head
        eye_radius = int(self.cell_size * SNAKE_HEAD_EYE_RADIUS_RATIO)
        pupil_radius = int(self.cell_size * SNAKE_HEAD_PUPIL_RADIUS_RATIO)
        
        # Simple eye placement, not considering direction for now
        eye_offset_x = segment_radius // 2
        eye_offset_y = segment_radius // 2 # Place eyes slightly towards top

        eye1_pos = (head_center_x - eye_offset_x // 1.5, head_center_y - eye_offset_y)
        eye2_pos = (head_center_x + eye_offset_x // 1.5, head_center_y - eye_offset_y)
        
        pygame.draw.circle(self.screen, COLOR_SNAKE_EYE, eye1_pos, eye_radius)
        pygame.draw.circle(self.screen, COLOR_SNAKE_EYE, eye2_pos, eye_radius)
        pygame.draw.circle(self.screen, COLOR_SNAKE_PUPIL, eye1_pos, pupil_radius)
        pygame.draw.circle(self.screen, COLOR_SNAKE_PUPIL, eye2_pos, pupil_radius)
        
        # Draw tail segments
        darker_color_factor = 0.7
        darker_color = (int(color[0] * darker_color_factor), 
                        int(color[1] * darker_color_factor), 
                        int(color[2] * darker_color_factor))
        
        for segment in snake.tail:
            tail_row, tail_col = segment
            tail_center_x = tail_col * self.cell_size + self.cell_size // 2
            tail_center_y = tail_row * self.cell_size + self.cell_size // 2
            pygame.draw.circle(self.screen, darker_color, (tail_center_x, tail_center_y), segment_radius)

    def draw_side_panel(self, turn, eliminated_snakes_ids, num_total_snakes):
        panel_x_start = self.game_board_width
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, (panel_x_start, 0, PANEL_WIDTH, self.window_height))
        
        current_y = 20
        line_spacing = 30
        small_line_spacing = 20
        color_swatch_size = 15

        # Title
        title_text = self.font_panel_header.render("Game Info", True, COLOR_PANEL_TEXT)
        self.screen.blit(title_text, (panel_x_start + (PANEL_WIDTH - title_text.get_width()) // 2, current_y))
        current_y += line_spacing + 10

        # Turn Info
        turn_text_surf = self.font_panel_text.render(f"Turn: {turn}", True, COLOR_PANEL_TEXT)
        self.screen.blit(turn_text_surf, (panel_x_start + 20, current_y))
        current_y += line_spacing

        # Model Controlled Snake
        model_snake_text = self.font_panel_text.render("Model Snake:", True, COLOR_PANEL_TEXT)
        self.screen.blit(model_snake_text, (panel_x_start + 20, current_y))
        current_y += small_line_spacing
        
        model_snake_color = self.get_snake_color(self.model_idx)
        pygame.draw.rect(self.screen, model_snake_color, (panel_x_start + 25, current_y, color_swatch_size, color_swatch_size))
        model_id_text = self.font_model_snake.render(f" ID: {self.model_idx}", True, COLOR_MODEL_SNAKE_HIGHLIGHT)
        self.screen.blit(model_id_text, (panel_x_start + 25 + color_swatch_size + 5, current_y -2)) # Slightly adjust y for alignment
        current_y += line_spacing

        # Active Snakes (Optional, could be many)
        # active_snakes_text = self.font_panel_text.render("Active Snakes:", True, COLOR_PANEL_TEXT)
        # self.screen.blit(active_snakes_text, (panel_x_start + 20, current_y))
        # current_y += small_line_spacing
        # # This would require knowing all snake objects, not just eliminated ones from state
        # for i in range(num_total_snakes):
        #     if i not in eliminated_snakes_ids:
        #         s_color = self.get_snake_color(i)
        #         pygame.draw.rect(self.screen, s_color, (panel_x_start + 25, current_y, color_swatch_size, color_swatch_size))
        #         id_text = self.font_panel_text.render(f" ID: {i}", True, COLOR_PANEL_TEXT)
        #         self.screen.blit(id_text, (panel_x_start + 25 + color_swatch_size + 5, current_y -2))
        #         current_y += small_line_spacing
        # current_y += 10 # Extra space

        # Eliminated Snakes
        elim_header_text = self.font_panel_text.render("Eliminated Snakes:", True, COLOR_PANEL_TEXT)
        self.screen.blit(elim_header_text, (panel_x_start + 20, current_y))
        current_y += small_line_spacing
        
        if eliminated_snakes_ids:
            for snake_id in eliminated_snakes_ids:
                if current_y + small_line_spacing > self.window_height - 20: # Avoid drawing off panel
                    break
                elim_snake_color = self.get_snake_color(snake_id)
                pygame.draw.rect(self.screen, elim_snake_color, (panel_x_start + 25, current_y, color_swatch_size, color_swatch_size))
                elim_id_text = self.font_panel_text.render(f" ID: {snake_id}", True, COLOR_PANEL_TEXT)
                self.screen.blit(elim_id_text, (panel_x_start + 25 + color_swatch_size + 5, current_y-2))
                current_y += small_line_spacing
        else:
            none_text = self.font_panel_text.render("  None", True, COLOR_PANEL_TEXT)
            self.screen.blit(none_text, (panel_x_start + 20, current_y))
            current_y += small_line_spacing


    def visualize_state(self, state):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        self.update_dimensions(state.board_width, state.board_height)
        
        # Clear game board area (everything to the left of the panel)
        self.screen.fill(COLOR_BOARD_DARK, (0, 0, self.game_board_width, self.game_board_height))
        
        self.draw_grid()
        
        for apple_obj in state.apples:
            self.draw_apple(apple_obj.position)
        
        for i, snake in enumerate(state.snakes):
            # The 'state' object should ideally indicate if a snake is alive.
            # Assuming 'state.snakes' only contains active snakes or 'snake' object has an 'is_eliminated' flag.
            # For now, we draw all snakes passed in 'state.snakes'.
            # The 'eliminated_snakes' list in 'state' is used for the panel.
            self.draw_snake(snake, i) # Pass snake index for color
                 
        # Draw the side panel
        # We need to know the total number of snakes that started to list all, or just use IDs from state.snakes
        num_total_snakes_in_current_state = len(state.snakes) # This might not be the initial total
        self.draw_side_panel(state.turn, state.eliminated_snakes, num_total_snakes_in_current_state) # Pass necessary info
        
        pygame.display.flip()
        self.clock.tick(10) # Increased FPS slightly for smoother visuals
    
    def close(self):
        pygame.quit()

# --- Example Usage (assuming a mock 'state' object) ---
if __name__ == '__main__':
    # Mock classes for Snake and Apple to run the visualizer independently
    class MockSnake:
        def __init__(self, head_pos, tail_segments):
            self.head = head_pos  # [row, col]
            self.tail = tail_segments  # list of [row, col]

    class MockApple:
        def __init__(self, position):
            self.position = position  # [row, col]

    class MockGameState:
        def __init__(self, width, height, turn, model_idx):
            self.board_width = width
            self.board_height = height
            self.turn = turn
            self.apples = []
            self.snakes = []
            self.eliminated_snakes = [] # List of eliminated snake IDs
            self.whoose_prev_turn = None # Not explicitly used in new UI drawing but was in old

            # Example: Create a few snakes
            self.snakes.append(MockSnake([height // 2, width // 2 -1], [[height // 2, width // 2 - 2], [height // 2, width // 2 - 3]]))
            if width > 6 and height > 6 :
                 self.snakes.append(MockSnake([2,2], [[2,1]]))
                 self.snakes.append(MockSnake([height-3,width-3], [[height-3,width-4]]))


            # Example: Create a few apples
            self.apples.append(MockApple([height // 4, width // 4]))
            if width > 5 and height > 5:
                self.apples.append(MockApple([height * 3 // 4, width * 3 // 4]))
            
            # Example: Mark one snake as eliminated for demonstration
            if len(self.snakes) > 2:
                 self.eliminated_snakes = [2] # ID of the third snake (index 2)


    # --- Initialize and run ---
    BOARD_SIZE_W = 15
    BOARD_SIZE_H = 15
    CELL_S = 25 # Adjusted cell size for a reasonable game board display
    MODEL_CONTROLLED_SNAKE_ID = 0 # Let's say model controls snake 0

    visualizer = GameVisualizer(MODEL_CONTROLLED_SNAKE_ID, BOARD_SIZE_W, BOARD_SIZE_H, CELL_S)
    
    current_turn = 0
    game_state = MockGameState(BOARD_SIZE_W, BOARD_SIZE_H, current_turn, MODEL_CONTROLLED_SNAKE_ID)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN: # Simple interaction for demo
                if event.key == pygame.K_SPACE:
                    current_turn += 1
                    game_state.turn = current_turn
                    # Simulate snake movement (very basic)
                    for i, s in enumerate(game_state.snakes):
                        if i not in game_state.eliminated_snakes:
                            old_head = list(s.head)
                            s.head[1] = (s.head[1] + 1) % BOARD_SIZE_W # Move right
                            s.tail.insert(0, old_head)
                            if len(s.tail) > 3: # Keep tail length limited
                                s.tail.pop()
                    # Randomly eliminate a snake for demo
                    if current_turn % 5 == 0 and len(game_state.snakes) > len(game_state.eliminated_snakes):
                        for i in range(len(game_state.snakes)):
                            if i not in game_state.eliminated_snakes:
                                game_state.eliminated_snakes.append(i)
                                break
        
        visualizer.visualize_state(game_state)

    visualizer.close()
    sys.exit()