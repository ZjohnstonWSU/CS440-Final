from pieces import ChessPiece
from constants import *
from evaluation import *
import math
from copy import deepcopy
import random

# Initialize global variables
board = [[None for _ in range(8)] for _ in range(8)]
current_player = 'White'
selected_piece = None
selected_pos = None
game_started = False
game_over_message = None
max_depth = 3
selected_algorithm = 'Minimax' # Default algorithm
selected_color = "White" # Default Color

# Place initial pieces on board
def init_board():
    global current_player

    # Reset the board to remove all previous pieces (Used if game is reset)
    for row in range(8):
        for col in range(8):
            board[row][col] = None

    # Fill pawn lines
    for col in range(8):
        board[1][col] = ChessPiece('Black', 'pawn', f'../images/black_pawn.png')
        board[6][col] = ChessPiece('White', 'pawn', f'../images/white_pawn.png')

    # Fill backlines
    positions = [('rook', [0, 7]), ('knight', [1, 6]), ('bishop', [2, 5]), ('queen', [3]), ('king', [4])]
    for piece, cols in positions:
        for col in cols:
            board[0][col] = ChessPiece('Black', piece, f'../images/black_{piece}.png')
            board[7][col] = ChessPiece('White', piece, f'../images/white_{piece}.png')
    
    # Reverse board if user plays as "Black"
    if selected_color == "Black":
        board.reverse()
        for row in board:
            row.reverse()
        # Set correct color for player
        current_player = 'White'
    else:
        current_player = 'White'

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

    # Add algorithm selection buttons
    algorithm_text = font.render("Algorithm", True, WHITE)
    screen.blit(algorithm_text, (HEIGHT + 25, 250))  # Adjust the y-offset as needed

    algorithms = ['Minimax', 'Monte Carlo']
    y_offset = 290  # Start below the "Algorithm" label
    for algorithm in algorithms:
        # Highlight the selected algorithm in green
        text_color = GREEN if selected_algorithm == algorithm else WHITE
        button_text = font.render(algorithm, True, text_color)
        screen.blit(button_text, (HEIGHT + 25, y_offset))
        y_offset += 40  # Increment y-offset for the next button

    # Difficulty settings label and buttons
    difficulty_text = font.render("Difficulty", True, WHITE)
    screen.blit(difficulty_text, (HEIGHT + 25, 75))

    # Difficulty buttons
    difficulties = ['Easy', 'Medium', 'Hard']
    y_offset = 115
    for difficulty in difficulties:
        # Set text color to green if it's the selected difficulty, otherwise white
        text_color = GREEN if selected_difficulty == difficulty else WHITE
        button_text = font.render(difficulty, True, text_color)
        screen.blit(button_text, (HEIGHT + 25, y_offset))
        y_offset += 40  # Increment y_offset for the next button

    # Draw "Play as" selection (to choose to play as Black or White)
    play_as_text = font.render("Play As", True, WHITE)
    screen.blit(play_as_text, (HEIGHT + 25, 400))  # Adjust the y-offset as needed

    # Color Selection Button
    piece_colors = ['White', 'Black']
    y_offset = 440  # Start below the "Play As" label
    for piece_color in piece_colors:
        # Highlight the selected color in green
        text_color = GREEN if selected_color == piece_color else WHITE
        button_text = font.render(piece_color, True, text_color)
        screen.blit(button_text, (HEIGHT + 25, y_offset))
        y_offset += 40  # Increment y-offset for the next button

    # Draw "Reset" button
    reset_button_text = font.render("Reset", True, WHITE)
    reset_button_y = HEIGHT - 60
    screen.blit(reset_button_text, (HEIGHT + 25, reset_button_y))

    # Only a valid string if game end has not been reached
    if game_over_message:
        lines = game_over_message.split("\n")
        y_offset = 20
        for line in lines:
            text = font.render(line, True, RED)
            screen.blit(text, (HEIGHT + 20, y_offset))
            y_offset += 40
    
    # Draw the Start Game button if the game hasn't started
    elif not game_started:
        font = pygame.font.Font(None, 36)
        text = font.render("Start Game", True, WHITE)
        screen.blit(text, (HEIGHT + 25, 25))
    
    else:
        text = font.render(f"{current_player.capitalize()}'s Turn", True, BLACK)
        screen.blit(text, (HEIGHT + 20, 20))
        if is_check(current_player, board):
            check_text = font.render("In Check!", True, RED)
            screen.blit(check_text, (HEIGHT + 20, 60))

def chess_notation(i, j):
    row = 8 - i  # Convert top-to-bottom index to standard 1-8
    column = chr(j + ord('a'))  # Convert left-to-right index to 'a'-'h'
    return f"{column}{row}"

def board_indices(notation):
    column = notation[0]
    row = int(notation[1])
    
    i = 8 - row  # Convert chess row to 0-indexed row
    j = ord(column) - ord('a')  # Convert chess column to 0-indexed column
    
    return (i, j)

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
    current_player = 'Black' if current_player == 'White' else 'White'

    # Check for checkmate
    if is_check(current_player, board) and is_game_over(board):
        winner = 'Black' if current_player == 'White' else 'White'
        game_over_message = f"Checkmate!\n{winner.capitalize()} wins!"

def getCopyOfBoard():
    tempBoard = [[None for _ in range(8)] for _ in range(8)]
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if not piece is None:
                tempBoard[i][j] = ChessPiece(piece.color, piece.type, f'../images/{piece.color}_{piece.type}.png')
            else:
                tempBoard[i][j] = None
    return tempBoard

def getMonteCarloBoard():
    tempBoard = [[None for _ in range(8)] for _ in range(8)]
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece is not None:
                tempBoard[i][j] = ChessPiece(piece.color, piece.type, None)
            else:
                tempBoard[i][j] = None
    return tempBoard

def make_move_temp(start_pos, end_pos, tempBoard):
    global current_player, game_over_message
    piece = tempBoard[start_pos[0]][start_pos[1]]
    tempBoard[end_pos[0]][end_pos[1]] = piece
    tempBoard[start_pos[0]][start_pos[1]] = None

    if not piece is None and piece.type == 'pawn' and (end_pos[0] == 0 or end_pos[0] == 7):
        tempBoard[end_pos[0]][end_pos[1]] = ChessPiece(piece.color, 'queen', f'../images/{piece.color}_queen.png')

def undo_move(tempBoard, move):
    start_pos, end_pos = move
    piece = tempBoard[end_pos[0]][end_pos[1]]
    tempBoard[start_pos[0]][start_pos[1]] = piece
    tempBoard[end_pos[0]][end_pos[1]] = None

def minimax(tempBoard, depth, alpha, beta, maximizing_player):
    if depth == 0 or is_game_over(tempBoard):
        evulate = evaluate_board(tempBoard)
        return evulate, None

    # Determine which color the AI is playing as
    ai_color = 'Black' if selected_color == 'White' else 'White'

    if maximizing_player:
        max_eval = -math.inf
        best_move = None
        for move in get_all_moves(tempBoard, ai_color):  # Assuming AI is playing as Black
            make_move_temp(move[0], move[1], tempBoard)
            eval, _ = minimax(tempBoard, depth - 1, alpha, beta, False)
            undo_move(tempBoard, move)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        best_move = None
        for move in get_all_moves(tempBoard, selected_color):
            make_move_temp(move[0], move[1], tempBoard)
            eval, _ = minimax(tempBoard, depth - 1, alpha, beta, True)
            undo_move(tempBoard, move)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def monte_carlo(tempBoard, simulations):
    best_move = None
    best_score = -math.inf

    # Determine which color the AI is playing as
    ai_color = 'Black' if selected_color == 'White' else 'White'

    # Get all possible moves for the current player
    moves = get_all_moves(tempBoard, ai_color) # Assuming AI is playing as Black

    for move in moves:
        total_score = 0

        # Simulate games for the current move
        for _ in range(simulations):
            # Create a copy of the board for simulation
            simulated_board = deepcopy(getMonteCarloBoard())
            make_move_temp(move[0], move[1], simulated_board)

            # Play random moves until the game ends
            while not is_game_over(simulated_board):
                # Get all valid moves for the current player
                current_color = 'White' if current_player == 'Black' else 'Black'
                random_moves = get_all_moves(simulated_board, current_color)

                if not random_moves:
                    break

                random_move = random.choice(random_moves)
                make_move_temp(random_move[0], random_move[1], simulated_board)
            
            # Evaluate the final board state
            total_score += evaluate_board(simulated_board)

        # Calculate the average score for the current move
        average_score = total_score / simulations

        # Update the best move if the average score is better
        if average_score > best_score:
            best_score = average_score
            best_move = move

    return best_move

def get_all_moves(tempBoard, color):
    moves = []
    for row in range(8):
        for col in range(8):
            piece = tempBoard[row][col]
            if piece and piece.color == color:
                valid_moves = get_valid_moves(piece, row, col, tempBoard)
                for move in valid_moves:
                    moves.append(((row, col), move))
    return moves

def get_best_move(tempBoard):
    _, best_move = minimax(tempBoard, max_depth, -math.inf, math.inf, True)
    return best_move

# Update the pieces 
def draw_piece():
    if not game_started:  # Check if the game has started
        return

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                screen.blit(piece.image,(col*SQUARE_SIZE, row*SQUARE_SIZE))

# Get valid moves for a given piece
def get_valid_moves(piece, row, col, board, check_safety=True):
    moves = []

    # Compute moves based on piece type
    if piece.type == 'pawn':

        # Set direction based on the color the user is playing as
        if selected_color == "White":
            direction = -1 if piece.color == 'White' else 1
            start_row = 6 if piece.color == 'White' else 1  # Row from which the pawn can move two squares
        else:
            direction = 1 if piece.color == 'White' else -1
            start_row = 1 if piece.color == 'White' else 6  # Adjusted for reversed board

        #Normal move forward
        if 0 <= row + direction < 8 and board[row + direction][col] is None:
            moves.append((row + direction, col))
            # Double move from starting row
            if row == start_row and board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))
       
        #Capture a piece diagonally
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
        if not is_check(piece.color, board):
            legal_moves.append((r, c))

        # Undo the move
        board[row][col] = piece
        board[r][c] = temp_piece

    return legal_moves

# Check if the king is in check
def is_check(color, board):
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
                if king_pos in get_valid_moves(piece, r, c, board, check_safety=False):
                    return True
    return False       

# Check for checkmate by seeing if there are any valid moves left
def is_game_over(board):
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.color == current_player:
                valid_moves = get_valid_moves(piece,r,c, board)
                if valid_moves: return False
    return True

# Handle mouse clicks
def handle_click(pos):
    global selected_piece, selected_pos, valid_moves, current_player, game_over_message, selected_color

    if game_over_message:
        return

    col = pos[0] // SQUARE_SIZE
    row = pos[1] // SQUARE_SIZE

    # Check if the click is within the chessboard
    if 0 <= col < 8 and 0 <= row < 8:
        # If game has not started yet and chess board is clicked, return
        if not game_started:
            return
        
        # There is no piece selected yet, select piece user
        #   clicked on and calculate that piece's moves
        if selected_piece is None:
            piece = board[row][col]
            if piece and piece.color == current_player:
                selected_piece = piece
                selected_pos = (row, col)
                valid_moves = get_valid_moves(piece, row, col, board)
        # A piece is selected and user is trying to move to a
        #   space, carry out move if legal
        else:
            if (row, col) in valid_moves:
                make_move(selected_pos, (row, col))

                # Update board before processing AI input
                draw_board()
                draw_piece()
                pygame.display.update() 
                if not game_over_message and current_player != selected_color:
                    process_AI_input()
            selected_piece = None
            selected_pos = None
            valid_moves = []
    elif HEIGHT <= pos[0] < WIDTH:  # Click within the sidebar
        sidebar_click(pos)
    else:
        # Ignore other clicks
        return
    
def process_AI_input():
    global selected_algorithm, selected_difficulty
    if selected_algorithm == 'Minimax':
        ai_move = get_best_move(getCopyOfBoard())  # Use Minimax
    elif selected_algorithm == 'Monte Carlo':
        if selected_difficulty == 'Easy':
            simulations = 1
        elif selected_difficulty == 'Medium':
            simulations = 3
        elif selected_difficulty == 'Hard':
            simulations = 5
        else:
            simulations = 3 # Default to Medium

        ai_move = monte_carlo(getCopyOfBoard(), simulations)  # Use Monte Carlo
    else:
        ai_move = None  # Fallback in case no algorithm is selected

    if ai_move:
        make_move(ai_move[0], ai_move[1]) 
    return

# Handle sidebar mouse clicks (called from "handle_click" function) 
def sidebar_click(pos):
    global game_started, selected_difficulty, current_player, max_depth, selected_color

    button_height = 40
    button_width = WIDTH - HEIGHT
    button_x = HEIGHT
    button_y = 0

    # Start Game button properties
    start_game_button_x = HEIGHT + 25
    start_game_button_y = 25
    start_game_button_width = 150
    start_game_button_height = 40

    start_game_button_rect = pygame.Rect(start_game_button_x, start_game_button_y, start_game_button_width, start_game_button_height)

    # Check if the click is within the "Start Game" button bounds
    if start_game_button_rect.collidepoint(pos):
        game_started = True
        init_board()  # Initialize the board when "Start Game" is clicked
        draw_board()  # Redraw board to reflect the initial piece placements
        draw_piece()
        pygame.display.update()

        if selected_color == "Black":
            process_AI_input()
            draw_board()
            draw_piece()
            pygame.display.update()

    # Algorithm button properties
    algorithms = {'Minimax': 290, 'Monte Carlo': 330}  # y-offsets for each button
    algorithm_button_width = 150
    algorithm_button_x = HEIGHT + 25
    algorithm_button_height = 40

    # Check if an algorithm button was clicked
    for algorithm, y_offset in algorithms.items():
        # Define the rectangle for each algorithm button
        algorithm_button_rect = pygame.Rect(algorithm_button_x, y_offset, algorithm_button_width, algorithm_button_height)

        # Check if the click is within the bounds of any algorithm button
        if algorithm_button_rect.collidepoint(pos):
            global selected_algorithm
            selected_algorithm = algorithm  # Update the selected algorithm

    # Difficulty button properties
    difficulties = {'Easy': 115, 'Medium': 155, 'Hard': 195}  # y-offsets for each button
    difficultiesMaxDepth = {'Easy': 3, 'Medium': 5, 'Hard': 7}  # y-offsets for each button
    difficulty_button_width = 150
    difficulty_button_x = HEIGHT + 25
    difficulty_button_height = 40

    # Check if a difficulty button was clicked
    for difficulty, y_offset in difficulties.items():
        # Define the rectangle for each difficulty button
        difficulty_button_rect = pygame.Rect(difficulty_button_x, y_offset, difficulty_button_width, difficulty_button_height)

        # Check if the click is within the bounds of any difficulty button
        if difficulty_button_rect.collidepoint(pos):
            selected_difficulty = difficulty  # Update the global difficulty variable
            max_depth = difficultiesMaxDepth[difficulty]


    # Define y-offsets for each color under "Play As"
    play_as_colors = {'White': 440, 'Black': 480}  # y-offsets for each color
    play_as_button_width = 150
    play_as_button_x = HEIGHT + 25
    play_as_button_height = 40

    # "Play As" button click handling
    for color, y_offset in play_as_colors.items():
        # Define the rectangle for each color button
        play_as_button_rect = pygame.Rect(play_as_button_x, y_offset, play_as_button_width, play_as_button_height)

        # Check if the click is within the bounds of any color button - disabled if game is already started
        if play_as_button_rect.collidepoint(pos) and game_started == False:
            selected_color = color  # Update the selected color
            draw_board()  # Redraw the board to reflect the new selected color
            break  # Break the loop once a color is selected

    # Reset button position and dimensions
    reset_button_x = HEIGHT + 25
    reset_button_y = HEIGHT - 60
    reset_button_width = 150
    reset_button_height = 40

    reset_button_rect = pygame.Rect(reset_button_x, reset_button_y, reset_button_width, reset_button_height)
    if reset_button_rect.collidepoint(pos):
        init_board()
        game_started = False
        current_player = 'White'

    return
