def is_on_board(row, col):
    """checks if a given position is within bounds on the board"""
    if 0 <= row < 8: # row is within bounds
        if 0 <= col < 8: # col is within bounds
            return True
    return False # not within bounds
def get_piece_at_position(board, position):
    """receives piece at a specific position"""
    # iterate through the pieces in the board
    for piece in board:
        if piece[2] == position: # check if the current piece being iterated over is the desired position
            return piece
    return None # piece not found
def generate_moves_for_piece(piece, board, color):
    """generate all legal moves for a piece given its type and position"""
    row, col = piece[2] # store the position of the piece
    piece_type = piece[0] # store the type of the piece
    legal_moves = []
    # logic for how many spaces and what directions the pieces move
    directions = {
        'Rook': [(0, 1), (1, 0), (0, -1), (-1, 0)],
        'Bishop': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
        'Knight': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
        'King': [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (-1, 1)],
        'Squire': [(2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, 1), (1, -1), (-1, -1)],
        'Combatant': [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    }
    # iterate over the directions of a certain piece
    for move_row, move_col in directions[piece_type]:
        # calculate the new position
        new_row, new_col = row + move_row, col + move_col
        # this loop runs while we are within the bounds of the board and the pieces are rooks or bishops (which can move multiple squares in one direction) or the other pieces (where we consider the next immediate square)
        while is_on_board(new_row, new_col) and (piece_type in ['Rook', 'Bishop'] or (new_row, new_col) == (row + move_row, col + move_col)):
            target_piece = get_piece_at_position(board, (new_row, new_col)) # check for piece at new position
            if target_piece:
                if target_piece[1] != color: # not our piece
                    if not (piece_type == 'Combatant' and (abs(move_row), abs(move_col)) != (1, 1)): # ensures the piece is not a combatant trying to move diagonally
                        legal_moves.append(((row, col), (new_row, new_col))) # legal move (can capture)
                break
            else: # new position is not occupied
                if not (piece_type == 'Combatant' and (abs(move_row), abs(move_col)) == (1, 1)): # ensures the piece is not a combatant trying to move diagonally
                    legal_moves.append(((row, col), (new_row, new_col)))# legal move
            new_row += move_row # increment row
            new_col += move_col # increment col
    return legal_moves
def get_legal_moves(board, color):
    """collects all legal moves for all pieces of a given color"""
    capture_moves = [] # empty list to store the moves where we capture opponent's pieces
    other_moves = [] # empty list to store every other valid move
    # iterate through the pieces in the board
    for piece in board:
        # check pieces of our color only, which is white
        if piece[1] == color:
            for move in generate_moves_for_piece(piece, board, color): # generate moves for each of our pieces
                if get_piece_at_position(board, move[1]): # checks if there is an opponent piece or no piece
                    capture_moves.append(move) # store moves where you can capture opponent's piece
                else:
                    other_moves.append(move) # if generate_moves_for_piece returns None, then that means there is an empty space, so we store this valid move
    return capture_moves + other_moves # append the two lists to have a list of tuples with all legal moves. append capture_moves first to prioritize maximizing our score by capturing opponent's pieces
def opposite_color(color):
    """returns the opposite color"""
    # return black if the given color is white
    if color == "white":
        return "black"
    return "white" # return white otherwise
def apply_move(board, move):
    """applies a move to the chessboard and updates the board accordingly"""
    start_pos, end_pos = move # store the starting position and ending position of the piece in the board
    moving_piece = get_piece_at_position(board, start_pos) # get the piece we want to move at its current board position
    # desired piece not found, so return the current board state
    if not moving_piece:
        return board
    
    new_board = [] # empty list to store tuples as we apply moves for our desired piece
    # iterate through each piece in the board
    for piece in board:
        if piece[2] != start_pos and piece[2] != end_pos: # other pieces that are not the pieces we want to move
            new_board.append(piece) # append all other pieces
    new_board.append((moving_piece[0], moving_piece[1], end_pos)) # append the piece we want to move at its new position
    return new_board # return the new board state
def evaluate_board(board, color):
    """assigns a score (heuristic) to the board for a given color"""
    # reasonable piece values
    piece_values = {'King': 99999999, 'Rook': 5, 'Knight': 3, 'Bishop': 3, 'Squire': 3, 'Combatant': 2}
    
    # check if the white king exists on the board
    white_king_exists = False
    for piece in board:
        if piece[0] == 'King' and piece[1] == 'white':
            white_king_exists = True
    # check if the black king exists on the board
    black_king_exists = False
    for piece in board:
        if piece[0] == 'King' and piece[1] == 'black':
            black_king_exists = True
    
    # white king does not exist, which means black wins
    if not white_king_exists:
        return -99999999
        
    # black king does not exist, which means white wins
    if not black_king_exists:
        return 99999999
    
    # if both kings are on the board, then we evaluate scores to calculate who has the advantage
    score = 0 # initialize score
    opponent_color = opposite_color(color) # get opponent's color
    # iterate through each piece on the board
    for piece in board:
        piece_value = piece_values.get(piece[0], 0) # gets value of the piece from the piece_values dicitonary
        # check if piece in board is our color and add its value to the score
        if piece[1] == color:
            score += piece_value
            # generate moves for our piece and iterate over these moves
            for move in generate_moves_for_piece(piece, board, color):
                target_piece = get_piece_at_position(board, move[1]) # check if any of the moves for our piece result in the capture of our opponent's piece
                # verify if the piece we want to capture is the opponent's piece
                if target_piece and target_piece[1] == opponent_color:
                    score += piece_values.get(target_piece[0], 0) * 0.5 # multiply by 0.5 to account for winning material
        else: # piece on board belongs to opponent
            score -= piece_value # subtract from overall score
    return score
def is_end_of_game(board):
    """checks presence of kings to determine end of the game"""
    kings = [] # empty list to store both kings
    # iterate through each piece in the board
    for piece in board:
        if piece[0] == 'King': # check if piece we iterate over is a king
            kings.append(piece) # append king to our list
    return len(kings) < 2 # if this condition holds, then that means the game is over because a player loses once they no longer have their king piece
def alpha_beta(board, depth, alpha, beta, maximizingPlayer, color):
    """implements alpha beta pruning to find the best move"""
    # base case
    if depth == 0 or is_end_of_game(board):
        return evaluate_board(board, color), None # return the score of the leaf node and None because no move is made at a leaf node
    # get all legal moves
    legal_moves = get_legal_moves(board, color)
    if maximizingPlayer: # maximizing player
        value = float('-inf') # initialize value to negative infinity
        best_move = None # initialize best_move to None
        # iterate through each legal move
        for move in legal_moves:
            new_board = apply_move(board, move) # apply the legal move
            eval, _ = alpha_beta(new_board, depth - 1, alpha, beta, False, opposite_color(color)) # evaluate its board state and call alpha_beta recursively with decreased depth and switch to our opponent who is the minimizing player
            if eval > value: # the current board state's eval is greater than the previous, so update the value and best_move
                value = eval # update eval
                best_move = move # update best_move
            alpha = max(alpha, eval) # update alpha to the maximum of itself and the new eval
            # break if beta is less than or equal to alpha because additional pruning is unnecessary
            if beta <= alpha:
                break
        return value, best_move
    else: # minimizing player
        value = float('inf') # initialize value to infinity
        best_move = None # initialize best_move to None
        # iterate through each legal move
        for move in legal_moves:
            new_board = apply_move(board, move) # apply the legal move
            eval, _ = alpha_beta(new_board, depth - 1, alpha, beta, True, opposite_color(color)) # evaluate its board state and call alpha_beta recursively with decreased depth and switch to our opponent who is the maximizing player
            if eval < value: # the current board state's eval is less than than the previous, so update the value and best_move
                value = eval # update eval
                best_move = move # update best_move
            beta = min(beta, eval) # update beta to the minimum of itself and the new eval
            # break if alpha is greater than or equal to alpha because additional pruning is unnecessary
            if alpha >= beta:
                break
        return value, best_move
def studentAgent(board):
    """essentially a wrapper for the alpha beta algorithm"""
    _, best_move = alpha_beta(board, 4, float('-inf'), float('inf'), True, 'white') # call alpha_beta with a depth of 4 to look 5 moves ahead
    return best_move
    
def find_best_move(board):
    """calls studentAgent"""
    return studentAgent(board)

m1_1 = [("Combatant", 'white', (0,5)),
("Rook", "white", (1,1)),
("Combatant", "white", (1,4)),
("King", "black", (1,5)),
("Combatant", "white", (1,6)),
("Squire", "white", (1,7)),
("Combatant", "white", (2,5)),
("Rook", "black", (4,3)),
("King", "white", (5,2)),
("Rook", "white", (6,5)),
("Bishop", "black", (7,0)),
("Bishop", "black", (7,3))
]
'''
find_best_move(m1_1) = ((1, 7), (1, 5))
'''

m3_1 = [("King", 'white', (7,7)),
("King", 'black', (0,0)),
("Rook", 'white', (6,1)),
("Rook", 'white', (5,1)),
("Rook", 'black', (6,5)),
("Rook", 'black', (6,6))]
'''
find_best_move(m3_1) = ((5, 1), (5, 0))
'''

m5_1 = [("King", 'white', (2,3)),
("King", 'black', (0,4)),
("Combatant", 'white', (1,4)),
("Combatant", 'white', (2,5)),
("Combatant", 'black', (7,0))]
'''
find_best_move(m5_1) = ((2, 3), (2, 4))
'''

e3_1 = [("King", "black", (0,4)),
("Rook", "black", (4,4)),
("King", "white", (2,3)),
("Squire", "white", (2,2))]
'''
studentAgent(e3_1) = ((2, 2), (2, 4))
'''

e3_2 = [("Rook", 'white', (0,2)),
("King", 'white', (1,2)),
("Rook", 'black', (3,0)),
("King", 'black', (6,2)),
("Rook", 'black', (6,4))]
'''
studentAgent(e3_2) = ((1, 2), (2, 1))
'''

print(find_best_move(m1_1))
print(find_best_move(m3_1))
print(find_best_move(m5_1))
print(find_best_move(e3_1))
print(find_best_move(e3_2))