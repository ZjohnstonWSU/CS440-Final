from pieces import ChessPiece
from constants import *

# Initialize global variables
board = [[None for _ in range(8)] for _ in range(8)]
current_player = 'white'
selected_piece = None
selected_pos = None
game_over_message = None

# Place initial pieces on board
def init_board():
    # Fill pawn lines
    for col in range(8):
        board[1][col] = ChessPiece('black', 'pawn', f'../images/black_pawn.png')
        board[6][col] = ChessPiece('white', 'pawn', f'../images/white_pawn.png')

    # Fill backlines
    positions = [('rook', [0, 7]), ('knight', [1, 6]), ('bishop', [2, 5]), ('queen', [3]), ('king', [4])]
    for piece, cols in positions:
        for col in cols:
            board[0][col] = ChessPiece('black', piece, f'../images/black_{piece}.png')
            board[7][col] = ChessPiece('white', piece, f'../images/white_{piece}.png')

# Draw updated board
def draw_board():
    # Fill square board backgrounds
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            # Highlight in green if a valid move for selected piece
            if selected_piece and (row, col) in valid_moves:
                pygame.draw.rect(screen, GREEN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

    # Highlight piece in yellow if selected
    if selected_pos:
        pygame.draw.rect(screen, YELLOW, (selected_pos[1] * SQUARE_SIZE, selected_pos[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)

    # Draw sidebar
    pygame.draw.rect(screen, GRAY, (HEIGHT, 0, WIDTH - HEIGHT, HEIGHT))
    font = pygame.font.Font(None, 36)

    # Only a valid string if game end has not been reached
    if game_over_message:
        lines = game_over_message.split("\n")
        y_offset = 20
        for line in lines:
            text = font.render(line, True, RED)
            screen.blit(text, (HEIGHT + 20, y_offset))
            y_offset += 40
    else:
        text = font.render(f"{current_player.capitalize()}'s Turn", True, BLACK)
        screen.blit(text, (HEIGHT + 20, 20))
        if is_check(current_player):
            check_text = font.render("In Check!", True, RED)
            screen.blit(check_text, (HEIGHT + 20, 60))

# Carry out move determined by start and end positions
def make_move(start_pos, end_pos):
    global current_player, game_over_message
    piece = board[start_pos[0]][start_pos[1]]
    board[end_pos[0]][end_pos[1]] = piece
    board[start_pos[0]][start_pos[1]] = None
    
    # Pawn promotion
    if piece.type == 'pawn' and (end_pos[0] == 0 or end_pos[0] == 7):
        board[end_pos[0]][end_pos[1]] = ChessPiece(piece.color, 'queen', f'../images/{piece.color}_queen.png')
    
    # Switch turns
    current_player = 'black' if current_player == 'white' else 'white'
    
    # Check for checkmate
    if is_check(current_player) and is_game_over():
        winner = 'black' if current_player == 'white' else 'white'
        game_over_message = f"Checkmate!\n{winner.capitalize()} wins!"

# Update the pieces 
def draw_piece():
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                screen.blit(piece.image,(col*SQUARE_SIZE, row*SQUARE_SIZE))

# Get valid moves for a given piece
def get_valid_moves(piece, row, col, check_safety=True):
    moves = []

    # Compute moves based on piece type
    if piece.type == 'pawn':
        direction = -1 if piece.color == 'white' else 1
        if 0 <= row + direction < 8 and board[row + direction][col] is None:
            moves.append((row + direction, col))
            if (piece.color == 'white' and row == 6) or (piece.color == 'black' and row == 1):
                if board[row + 2 * direction][col] is None:
                    moves.append((row + 2 * direction, col))
        for dc in [-1, 1]:
            if 0 <= row + direction < 8 and 0 <= col + dc < 8:
                if board[row + direction][col + dc] and board[row + direction][col + dc].color != piece.color:
                    moves.append((row + direction, col + dc))

    elif piece.type == 'rook':
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != piece.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r, c = r + dr, c + dc

    elif piece.type == 'knight':
        for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8 and (board[r][c] is None or board[r][c].color != piece.color):
                moves.append((r, c))

    elif piece.type == 'bishop':
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != piece.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r, c = r + dr, c + dc

    elif piece.type == 'queen':
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != piece.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r, c = r + dr, c + dc

    elif piece.type == 'king':
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8 and (board[r][c] is None or board[r][c].color != piece.color):
                    moves.append((r, c))

    # Skip king safety check if we're only checking attacking moves
    # Safety check makes sure that user doesn't miss that they're in check
    #   and makes a move that leaves their king vulnerable during opponent's turn
    if not check_safety:
        return moves

    # Filter moves that would leave the king in check
    legal_moves = []
    for r, c in moves:
        temp_piece = board[r][c]  # Store current piece
        board[r][c] = piece
        board[row][col] = None  # Temporarily move piece

        # Check if king is still safe
        if not is_check(piece.color):
            legal_moves.append((r, c))

        # Undo the move
        board[row][col] = piece
        board[r][c] = temp_piece

    return legal_moves

# Check if the king is in check
def is_check(color):
    king_pos = None
    for r in range(8):
        for c in range(8):
            if board[r][c] and board[r][c].color == color and board[r][c].type =='king':
                king_pos = (r,c)
                break
            if king_pos:
                break
    if not king_pos:
        return False

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.color != color:
                if king_pos in get_valid_moves(piece, r, c, check_safety=False):
                    return True
    return False       

# Check for checkmate by seeing if there are any valid moves left
def is_game_over():
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.color == current_player:
                valid_moves = get_valid_moves(piece,r,c)
                if valid_moves: return False
    return True

# Handle mouse clicks
def handle_click(pos):
    global selected_piece, selected_pos, valid_moves, current_player, game_over_message

    if game_over_message:
        return

    col = pos[0] // SQUARE_SIZE
    row = pos[1] // SQUARE_SIZE

    # There is no piece selected yet, select piece user
    #   clicked on and calculate that piece's moves
    if selected_piece is None:
        piece = board[row][col]
        if piece and piece.color == current_player:
            selected_piece = piece
            selected_pos = (row, col)
            valid_moves = get_valid_moves(piece, row, col)
    # A piece is selected and user is trying to move to a
    #   space, carry out move if legal
    else:
        if (row, col) in valid_moves:
            make_move(selected_pos, (row, col))
        selected_piece = None
        selected_pos = None
        valid_moves = []