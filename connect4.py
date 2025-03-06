import pygame
import random
import sys
import math
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
BOARD_SIZE = 7
CELL_SIZE = WINDOW_SIZE // (BOARD_SIZE + 2)
PIECE_SIZE = int(CELL_SIZE * 0.8)
DROPDOWN_PIECE_SIZE = 30  # Smaller size for dropdown previews
PLAYER_COLOR = (255, 50, 50)  # Brighter red
AI_COLOR = (50, 150, 255)     # Brighter blue
SHAPES = ['circle', 'square', 'triangle', 'diamond']
DROPDOWN_HEIGHT = 40
DROPDOWN_WIDTH = 150
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
AI_DELAY = 1.0  # seconds
ANIMATION_SPEED = 30  # Increased animation speed
PREVIEW_ALPHA = 128  # transparency for preview piece
HEADER_HEIGHT = 120  # Increased header height to accommodate title and dropdown

# Colors
BACKGROUND_COLOR = (25, 25, 35)  # Dark blue-gray
HEADER_COLOR = (35, 35, 45)      # Slightly lighter blue-gray
GRID_COLOR = (60, 60, 70)        # Light blue-gray
HOVER_COLOR = (70, 70, 80)       # Hover effect color
BUTTON_COLOR = (40, 180, 100)    # Modern green
BUTTON_HOVER_COLOR = (50, 200, 110)

# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + HEADER_HEIGHT))
pygame.display.set_caption('Connect 4 - Player vs AI')

# Initialize font
try:
    font = pygame.font.SysFont('sans-serif', 24)
    title_font = pygame.font.SysFont('sans-serif', 48)
except:
    font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 48)

class Piece:
    def __init__(self, color, shape, x, y):
        self.color = color
        self.shape = shape
        self.x = x
        self.y = y

class Connect4:
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.game_over = False
        self.winner = None
        self.win_type = None
        self.current_shape = 'circle'
        self.dropdown_open = False
        self.hovered_col = None
        print("Game initialized with shape:", self.current_shape)
        
    def drop_piece(self, col, is_player=True):
        if self.game_over:
            return False
            
        # Find the lowest empty cell in the column
        for row in range(BOARD_SIZE - 1, -1, -1):
            if self.board[row][col] is None:
                x = (col + 1) * CELL_SIZE
                y = (row + 1) * CELL_SIZE + HEADER_HEIGHT
                
                piece = Piece(
                    PLAYER_COLOR if is_player else AI_COLOR,
                    self.current_shape if is_player else random.choice(SHAPES),
                    x, y
                )
                self.board[row][col] = piece
                print(f"{'Player' if is_player else 'AI'} dropped piece at ({row}, {col}) with shape {piece.shape}")
                return True
        return False

    def check_winner(self, row, col):
        if self.board[row][col] is None:
            return False
            
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        piece = self.board[row][col]
        
        for dr, dc in directions:
            # Check color match
            color_count = 1
            shape_count = 1
            
            # Forward check
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] is not None:
                if self.board[r][c].color == piece.color:
                    color_count += 1
                if self.board[r][c].shape == piece.shape:
                    shape_count += 1
                r += dr
                c += dc
                
            # Backward check
            r, c = row - dr, col - dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] is not None:
                if self.board[r][c].color == piece.color:
                    color_count += 1
                if self.board[r][c].shape == piece.shape:
                    shape_count += 1
                r -= dr
                c -= dc
                
            if color_count >= 4:
                self.win_type = 'color'
                return True
            if shape_count >= 4:
                self.win_type = 'shape'
                return True
                
        return False

    def check_game_over(self, row, col):
        if self.check_winner(row, col):
            self.game_over = True
            self.winner = 'player' if self.board[row][col].color == PLAYER_COLOR else 'ai'
            print(f"Game Over! {self.winner.title()} wins by {self.win_type}!")
            return True
        return False

    def ai_move(self):
        print("AI is thinking...")
        time.sleep(AI_DELAY)
        
        # First, check if AI can win
        for col in range(BOARD_SIZE):
            for row in range(BOARD_SIZE - 1, -1, -1):
                if self.board[row][col] is None:
                    self.board[row][col] = Piece(AI_COLOR, random.choice(SHAPES), 0, 0)
                    if self.check_winner(row, col):
                        self.board[row][col] = None
                        print("AI found winning move!")
                        return self.drop_piece(col, False)
                    self.board[row][col] = None
                    break

        # Then, check if player can win and block
        for col in range(BOARD_SIZE):
            for row in range(BOARD_SIZE - 1, -1, -1):
                if self.board[row][col] is None:
                    self.board[row][col] = Piece(PLAYER_COLOR, self.current_shape, 0, 0)
                    if self.check_winner(row, col):
                        self.board[row][col] = None
                        print("AI blocking player's winning move!")
                        return self.drop_piece(col, False)
                    self.board[row][col] = None
                    break

        # If no immediate threats, make a random move
        available_cols = [col for col in range(BOARD_SIZE) if self.board[0][col] is None]
        if available_cols:
            print("AI making random move")
            return self.drop_piece(random.choice(available_cols), False)
        return False

def draw_piece(screen, piece, alpha=255, size=None):
    if piece is None:
        return
        
    # Use provided size or default to PIECE_SIZE
    piece_size = size if size is not None else PIECE_SIZE
    
    # Create a surface for the piece with alpha channel
    piece_surface = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
    
    # Draw shadow
    shadow_color = (*piece.color[:3], 100)
    if piece.shape == 'circle':
        pygame.draw.circle(piece_surface, shadow_color, 
                         (piece_size//2 + 2, piece_size//2 + 2), piece_size//2)
    elif piece.shape == 'square':
        pygame.draw.rect(piece_surface, shadow_color,
                        (2, 2, piece_size, piece_size))
    elif piece.shape == 'triangle':
        points = [
            (piece_size//2, 2),
            (2, piece_size - 2),
            (piece_size - 2, piece_size - 2)
        ]
        pygame.draw.polygon(piece_surface, shadow_color, points)
    elif piece.shape == 'diamond':
        points = [
            (piece_size//2, 2),
            (piece_size - 2, piece_size//2),
            (piece_size//2, piece_size - 2),
            (2, piece_size//2)
        ]
        pygame.draw.polygon(piece_surface, shadow_color, points)
    
    # Draw main piece
    piece_color = (*piece.color[:3], alpha)
    if piece.shape == 'circle':
        pygame.draw.circle(piece_surface, piece_color, 
                         (piece_size//2, piece_size//2), piece_size//2)
    elif piece.shape == 'square':
        pygame.draw.rect(piece_surface, piece_color,
                        (0, 0, piece_size, piece_size))
    elif piece.shape == 'triangle':
        points = [
            (piece_size//2, 0),
            (0, piece_size),
            (piece_size, piece_size)
        ]
        pygame.draw.polygon(piece_surface, piece_color, points)
    elif piece.shape == 'diamond':
        points = [
            (piece_size//2, 0),
            (piece_size, piece_size//2),
            (piece_size//2, piece_size),
            (0, piece_size//2)
        ]
        pygame.draw.polygon(piece_surface, piece_color, points)
    
    screen.blit(piece_surface, (piece.x - piece_size//2, piece.y - piece_size//2))

def draw_button(screen, text, x, y, width, height, color, hover_color):
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width, height)
    is_hovered = button_rect.collidepoint(mouse_pos)
    
    # Draw shadow
    shadow_rect = button_rect.copy()
    shadow_rect.x += 2
    shadow_rect.y += 2
    pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
    
    # Draw button with gradient effect
    pygame.draw.rect(screen, hover_color if is_hovered else color, button_rect)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 1)
    
    # Draw text with shadow
    text_shadow = font.render(text, True, (0, 0, 0))
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_shadow, (text_rect.x + 1, text_rect.y + 1))
    screen.blit(text_surface, text_rect)
    
    return button_rect

def draw_board(screen, game):
    # Draw gradient background
    screen.fill(BACKGROUND_COLOR)
    
    # Draw header with gradient effect
    header_surface = pygame.Surface((WINDOW_SIZE, HEADER_HEIGHT))
    header_surface.fill(HEADER_COLOR)
    screen.blit(header_surface, (0, 0))
    
    # Draw title with shadow
    title_text = "Connect 4"
    title_shadow = title_font.render(title_text, True, (0, 0, 0))
    title = title_font.render(title_text, True, (255, 255, 255))
    screen.blit(title_shadow, (WINDOW_SIZE//2 - title.get_width()//2 + 2, HEADER_HEIGHT//4 + 2))
    screen.blit(title, (WINDOW_SIZE//2 - title.get_width()//2, HEADER_HEIGHT//4))
    
    # Draw grid with modern look
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x = (col + 1) * CELL_SIZE
            y = (row + 1) * CELL_SIZE + HEADER_HEIGHT
            
            # Draw cell with modern style
            cell_rect = pygame.Rect(x - CELL_SIZE//2, y - CELL_SIZE//2, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRID_COLOR, cell_rect, 1)
            
            # Draw piece if exists
            if game.board[row][col]:
                draw_piece(screen, game.board[row][col])
    
    # Draw preview piece with glow effect
    if game.hovered_col is not None and not game.game_over:
        preview_x = (game.hovered_col + 1) * CELL_SIZE
        preview_y = HEADER_HEIGHT + CELL_SIZE//2
        preview_piece = Piece(PLAYER_COLOR, game.current_shape, preview_x, preview_y)
        draw_piece(screen, preview_piece, PREVIEW_ALPHA)

    # Draw modern shape selector (moved down)
    dropdown_x = WINDOW_SIZE//2 - DROPDOWN_WIDTH//2
    dropdown_y = HEADER_HEIGHT - DROPDOWN_HEIGHT - 10  # Adjusted position
    
    # Draw dropdown background with shadow
    shadow_rect = pygame.Rect(dropdown_x + 2, dropdown_y + 2, DROPDOWN_WIDTH, DROPDOWN_HEIGHT)
    pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
    
    # Draw main dropdown
    dropdown_rect = pygame.Rect(dropdown_x, dropdown_y, DROPDOWN_WIDTH, DROPDOWN_HEIGHT)
    pygame.draw.rect(screen, (255, 255, 255), dropdown_rect)
    pygame.draw.rect(screen, (200, 200, 200), dropdown_rect, 1)
    
    # Draw current shape with preview
    text = font.render(f"Shape: {game.current_shape}", True, (0, 0, 0))
    text_rect = text.get_rect(center=(dropdown_x + DROPDOWN_WIDTH//2, dropdown_y + DROPDOWN_HEIGHT//2))
    screen.blit(text, text_rect)
    
    # Draw shape preview with shadow (using smaller size)
    preview_piece = Piece(PLAYER_COLOR, game.current_shape, dropdown_x + DROPDOWN_WIDTH - 30, dropdown_y + DROPDOWN_HEIGHT//2)
    draw_piece(screen, preview_piece, size=DROPDOWN_PIECE_SIZE)
    
    # Draw dropdown options if open
    if game.dropdown_open:
        for i, shape in enumerate(SHAPES):
            if shape != game.current_shape:
                option_rect = pygame.Rect(dropdown_x, dropdown_y + (i+1)*DROPDOWN_HEIGHT, DROPDOWN_WIDTH, DROPDOWN_HEIGHT)
                pygame.draw.rect(screen, (255, 255, 255), option_rect)
                pygame.draw.rect(screen, (200, 200, 200), option_rect, 1)
                
                # Draw shape preview (using smaller size)
                preview_piece = Piece(PLAYER_COLOR, shape, dropdown_x + DROPDOWN_WIDTH - 30, dropdown_y + (i+1)*DROPDOWN_HEIGHT + DROPDOWN_HEIGHT//2)
                draw_piece(screen, preview_piece, size=DROPDOWN_PIECE_SIZE)
                
                text = font.render(shape, True, (0, 0, 0))
                text_rect = text.get_rect(center=(dropdown_x + DROPDOWN_WIDTH//2, dropdown_y + (i+1)*DROPDOWN_HEIGHT + DROPDOWN_HEIGHT//2))
                screen.blit(text, text_rect)

def main():
    game = Connect4()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                # Handle shape selector clicks
                dropdown_x = WINDOW_SIZE//2 - DROPDOWN_WIDTH//2
                dropdown_y = HEADER_HEIGHT - DROPDOWN_HEIGHT - 10
                
                if dropdown_x <= x <= dropdown_x + DROPDOWN_WIDTH and dropdown_y <= y <= dropdown_y + DROPDOWN_HEIGHT:
                    game.dropdown_open = not game.dropdown_open
                elif game.dropdown_open:
                    if dropdown_x <= x <= dropdown_x + DROPDOWN_WIDTH and dropdown_y <= y <= dropdown_y + (len(SHAPES) + 1) * DROPDOWN_HEIGHT:
                        selected_shape = SHAPES[(y - dropdown_y) // DROPDOWN_HEIGHT - 1]
                        if selected_shape != game.current_shape:
                            game.current_shape = selected_shape
                            game.dropdown_open = False
                
                # Handle game board clicks
                elif not game.game_over and y >= HEADER_HEIGHT:
                    col = round(x / CELL_SIZE - 1)
                    if 0 <= col < BOARD_SIZE:
                        if game.drop_piece(col, True):
                            # Check for winner after player move
                            for row in range(BOARD_SIZE):
                                if game.board[row][col] is not None:
                                    if not game.check_game_over(row, col):
                                        # Wait for 1 second before AI move
                                        pygame.display.flip()
                                        time.sleep(1.0)
                                        # AI move
                                        game.ai_move()
                                        # Check for winner after AI move
                                        for row in range(BOARD_SIZE):
                                            if game.board[row][col] is not None:
                                                game.check_game_over(row, col)
                                                break
                                    break
                
                # Handle play again button
                if game.game_over:
                    play_again_button = draw_button(screen, "Play Again", 
                                                  WINDOW_SIZE//2 - BUTTON_WIDTH//2,
                                                  WINDOW_SIZE//2 + 60,
                                                  BUTTON_WIDTH, BUTTON_HEIGHT,
                                                  BUTTON_COLOR, BUTTON_HOVER_COLOR)
                    if play_again_button.collidepoint(x, y):
                        game.reset_game()
            
            # Handle mouse motion for hover effects
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if y >= HEADER_HEIGHT and not game.game_over:
                    game.hovered_col = round(x / CELL_SIZE - 1)
                    if not 0 <= game.hovered_col < BOARD_SIZE:
                        game.hovered_col = None
                else:
                    game.hovered_col = None
                                
        draw_board(screen, game)
        
        # Draw game over overlay with blur effect
        if game.game_over:
            # Draw semi-transparent overlay with gradient
            overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE + HEADER_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            screen.blit(overlay, (0, 0))
            
            # Draw win message with shadow
            win_text = f"{game.winner.title()} wins by {game.win_type}!"
            text_shadow = title_font.render(win_text, True, (0, 0, 0))
            text = title_font.render(win_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
            screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
            screen.blit(text, text_rect)
            
            # Draw play again button
            draw_button(screen, "Play Again", 
                       WINDOW_SIZE//2 - BUTTON_WIDTH//2,
                       WINDOW_SIZE//2 + 60,
                       BUTTON_WIDTH, BUTTON_HEIGHT,
                       BUTTON_COLOR, BUTTON_HOVER_COLOR)
            
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main() 