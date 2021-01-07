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
    if 0 < piece < 12:
        if piece <= 6:
            return piece
        else:
            return piece - 6
    else:
        return None

def piece_allegiance (piece):
    '''Return white king or black king'''
    if empty < piece <= black_king:
        if white_pawn <= piece <= black_king:
            return white_king
        else:
            return black_king
    else:
        return None

def init_board ():
    board = [empty for _ in range(8 * 8)]
    # Place the pawns
    for c in range(8):
        board[c + 8] = white_pawn
        board[63 - 8 - c] = black_pawn
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

def available_pawn_moves (board, index):
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

def available_bishop_moves (board, index):
    diagonal_deltas = (-9, -7, 9, 7)
    moves = []
    for di in diagonal_deltas:
        new_index = index + di
        while new_index in range(64) and board[new_index] == empty:
            moves.append(new_index)
            new_index += di
        if pieces_are_enemies(board[index], board[new_index]):
            moves.append(new_index)
    return moves

def available_knight_moves (board, index):
    leaping_deltas = (-6, 6, -10, 10, -15, 15, -17, 17)
    moves = []
    for di in leaping_deltas:
        new_index = index + di
        if new_index in range(64):
            if board[new_index] == empty or pieces_are_enemies(board[index], board[new_index]):
                moves += new_index
    return moves

def available_rook_moves (board, index):
    perpendicular_deltas = (-1, 1, -8, 8)
    moves = []
    for di in perpendicular_deltas:
        new_index = index + di
        while new_index in range(64) and board[new_index] == empty:
            moves.append(new_index)
            new_index += di
        if pieces_are_enemies(board[index], board[new_index]):
            moves.append(new_index)
    return moves

def available_queen_moves (board, index):
    rook = available_rook_moves(board, index)
    bish = available_bishop_moves(board, index)
    return rook + bishop

def available_king_moves (board, index):
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
        return p1_allegiance != p2_allegiance

def piece_available_moves (board, index) -> list:
    piece = piece_role(board[index])
    if piece == white_pawn:
        return available_pawn_moves(board, index)
    elif piece == white_bishop:
        return available_bishop_moves(board, index)
    elif piece == white_knight:
        return available_knight_moves(board, index)
    elif piece == white_rook:
        return available_rook_moves(board, index)
    elif piece == white_queen:
        return available_queen_moves(board, index)
    elif piece == white_king:
        return available_king_moves(board, index)
    else:
        raise ValueError('invalid piece')

def square_is_white (index):
    if index not in range(64):
        raise ValueError('index not in range of the board space')
    r = (index // 8) % 2
    c = index % 2
    return (r and c) or not (r or c) 

def print_ascii_checkers ():
    enders = range(7, 64, 8)
    for i in range(64):
        s = '##' if square_is_white(i) else '__'
        print(end=s)
        if i in enders:
            print()

print_ascii_checkers()
board = init_board()
print(piece_available_moves(board, 0))
