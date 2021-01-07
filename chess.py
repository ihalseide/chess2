#!/usr/bin/env python3

# Piece identifiers in the board
empty = 0
white_pawn = 1
white_bishop = 2
white_knight = 3
white_rook = 4
white_queen = 5
white_king = 6
black_pawn = 7
black_bishop = 8
black_knight = 9
black_rook = 10
black_queen = 11
black_king = 12

def piece_role (piece):
    '''Return the piece's role by converting it to the white team'''
    if white_pawn <= piece <= black_king:
        if piece > white_king:
            piece -= white_king
        return piece
    else:
        return None

def piece_allegiance (piece):
    '''Return white king or black king'''
    if white_pawn <= piece <= black_king:
        if white_pawn <= piece <= white_king:
            return white_king
        else:
            return black_king
    else:
        return None

def init_board () -> list:
    board = [empty for i in range(64)]
    # Place the pawns
    for i in range(8):
        board[i + 8] = white_pawn
        board[55 - i] = black_pawn
    # Place the rooks
    board[0] = white_rook
    board[7] = white_rook
    board[56] = black_rook
    board[63] = black_rook
    # Place the knights
    board[1] = white_knight
    board[6] = white_knight
    board[57] = black_knight
    board[62] = black_knight
    # Place the bishops
    board[2] = white_bishop
    board[5] = white_bishop
    board[58] = black_bishop
    board[61] = black_bishop
    # Place the queens
    board[4] = white_queen
    board[60] = black_queen
    # Place the kings
    board[3] = white_king
    board[59] = black_king
    return board

def pawn_deltas (board, index):
    piece = board[index]
    allegiance = piece_allegiance(piece)

    # White allegiance initial values
    forward, forward_2 = 8, 16
    diag_r, diag_l = 7, 9

    if allegiance == black_king:
        forward *= -1
        diag_r *= -1
        diag_l *= -1
        forward_2 *= -1

    forward += index
    diag_r += index
    diag_l += index
    forward_2 += index

    return forward, forward_2, diag_r, diag_l

def pawn_moves (board, index):
    # TODO: implement en-passant maybe as a special rule, not
    # in this function...
    available = []
    piece = board[index]
    forward, forward_2, diag_r, diag_l = pawn_deltas(board, index)
    # Moving forward 1 and 2 spaces
    if forward in range(64) and board[forward] == empty:
        available.append(forward)
        if (8 <= index <= 15) or (48 <= index <= 55):
            if forward_2 in range(64) and board[forward_2] == empty:
                # First move can be 2 spaces too
                available.append(forward_2)
    # Capturing diagonal one way
    if diag_r in range(64) and pieces_are_enemies(piece, board[diag_r]):
        available.append(diag_r)
    # Capturing diagonal the other way
    if diag_l in range(64) and pieces_are_enemies(piece, board[diag_l]):
        available.append(diag_l)
    return available

def bishop_moves (board, index):
    diagonal_deltas = (-9, -7, 9, 7)
    moves = []
    for di in diagonal_deltas:
        new_index = index + di
        while new_index in range(64) and board[new_index] == empty:
            moves.append(new_index)
            new_index += di
        if new_index in range(64) and pieces_are_enemies(board[index], board[new_index]):
            moves.append(new_index)
    return moves

def knight_moves (board, index):
    leaping_deltas = (-6, 6, -10, 10, -15, 15, -17, 17)
    moves = []
    for di in leaping_deltas:
        new_index = index + di
        if new_index in range(64):
            if board[new_index] == empty or pieces_are_enemies(board[index], board[new_index]):
                moves.append(new_index)
    return moves

def rook_moves (board, index):
    perpendicular_deltas = (-1, 1, -8, 8)
    moves = []
    for di in perpendicular_deltas:
        new_index = index + di
        while new_index in range(64) and board[new_index] == empty:
            moves.append(new_index)
            new_index += di
        if new_index in range(64) and pieces_are_enemies(board[index], board[new_index]):
            moves.append(new_index)
    return moves

def queen_moves (board, index):
    rook = rook_moves(board, index)
    bishop = bishop_moves(board, index)
    return rook + bishop

def king_moves (board, index):
    neighbor_deltas = (-1, 1, -8, 8, 7, 9, -7, -9)
    moves = []
    for di in neighbor_deltas:
        new_index = index + di
        if new_index in range(64):
            if board[new_index] == empty or pieces_are_enemies(board[index], board[new_index]):
                moves.append(new_index)
    return moves

def pieces_are_enemies (p1, p2):
    p1_allegiance = piece_allegiance(p1)
    p2_allegiance = piece_allegiance(p2)
    if None in (p1_allegiance, p2_allegiance):
        return False 
    else:
        return not (p1_allegiance == p2_allegiance)

def piece_moves (board, index) -> list:
    role = piece_role(board[index])
    if role == white_pawn:
        return pawn_moves(board, index)
    elif role == white_bishop:
        return bishop_moves(board, index)
    elif role == white_knight:
        return knight_moves(board, index)
    elif role == white_rook:
        return rook_moves(board, index)
    elif role == white_queen:
        return queen_moves(board, index)
    elif role == white_king:
        return king_moves(board, index)
    else:
        raise ValueError('invalid piece')

def piece_is_threatened_by (board, index, other_index):
    piece = board[index]
    other = board[other_index]
    return ((pieces_are_enemies(piece, other))
            and (index in piece_available_moves(board, other_index)))

def piece_threat_list (board, index):
    '''Return a list of indices of enemy pieces
    that threaten the given piece'''
    piece = board[index]
    result = []
    for i, _ in enumerate(board):
        if piece_is_threatened_by(board, index, i):
            result.append(i)
    return result

def find_piece (board, piece):
    for i, p in enumerate(board):
        if p == piece:
            return i

def king_is_in_check (board, king):
    '''[white_king | black_king] -> [True | False]'''
    king_index = find_piece(board, king)
    return piece_is_threatened(board, king_index)

def piece_is_threatened (board, index) -> bool:
    threats = piece_threat_list(board, index)
    return len(threats) > 0

def square_is_white (index):
    if index not in range(64):
        raise ValueError('index not in range of the board space')
    r = (index // 8) % 2
    c = index % 2
    return (r and c) or not (r or c) 

def print_board_nums (board):
    # THIS IS USEFUL FOR DEBUGGING
    print('(hexadecimal)')
    for i, x in enumerate(board):
        print(hex(x)[2:].upper(), end=' ')
        if i != 0 and (i+1) % 8 == 0:
            print()
    print()

def index_name (index):
    if index in range(64):
        row = index // 8
        col = index % 8
        letter = 'ABCDEFGH'[7 - col]
        return letter + str(row + 1)
    else:
        raise ValueError('index out of range')

def piece_name (piece) -> str:
    allegiance = 'white' if (piece_allegiance(piece) == white_king) else 'black'
    role = piece_role(piece)
    if role == white_pawn:
        role = 'pawn'
    elif role == white_bishop:
        role = 'bishop'
    elif role == white_knight:
        role = 'knight'
    elif role == white_rook:
        role = 'rook'
    elif role == white_queen:
        role = 'queen'
    elif role == white_king:
        role = 'king'
    else:
        role = str(role)
    return allegiance + ' ' + role

def piece_describe (board, index):
    piece = board[index]
    coord = index_name(index)
    if piece == empty:
        return '%s is empty' %(coord)
    else:
        name = piece_name(piece)
        moves = ' or '.join([index_name(x) for x in piece_moves(board, index)])
        if moves:
            return 'the %s at %s can move to %s' %(name, coord, moves)
        else:
            return 'the %s at %s can not move' %(name, coord)

#################################################################

#board = init_board()
board = [empty for i in range(64)]
board[28] = white_bishop

print(piece_describe(board, 28))
for i in piece_moves(board, 28):
    print_board_nums(board)
    board[i] = 0xF
#for i, p in enumerate(board):
#    print(piece_describe(board, i))

