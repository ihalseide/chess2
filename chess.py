# This file contains the main code and logic behind the game of Chess

# Use this formatting to avoid typing mistakes, since it is important that
# these numeric constants are correct
EMPTY, \
WHITE_PAWN, \
WHITE_BISHOP, \
WHITE_KNIGHT, \
WHITE_ROOK, \
WHITE_QUEEN, \
WHITE_KING, \
BLACK_PAWN, \
BLACK_BISHOP, \
BLACK_KNIGHT, \
BLACK_ROOK, \
BLACK_QUEEN, \
BLACK_KING \
= range(13)

def piece_role (piece):
    '''Return the piece's role by converting it to the white team'''
    if WHITE_PAWN <= piece <= BLACK_KING:
        if piece > WHITE_KING:
            piece -= WHITE_KING
        return piece
    else:
        return None

def piece_allegiance (piece):
    '''Return white king or black king'''
    if WHITE_PAWN <= piece <= BLACK_KING:
        if WHITE_PAWN <= piece <= WHITE_KING:
            return WHITE_KING
        else:
            return BLACK_KING
    else:
        return None

def init_board () -> list:
    board = [EMPTY for i in range(64)]
    # pawns
    for i in range(8):
        board[i + 8] = WHITE_PAWN
        board[55 - i] = BLACK_PAWN
    # rooks
    board[0] = WHITE_ROOK
    board[7] = WHITE_ROOK
    board[56] = BLACK_ROOK
    board[63] = BLACK_ROOK
    # knights
    board[1] = WHITE_KNIGHT
    board[6] = WHITE_KNIGHT
    board[57] = BLACK_KNIGHT
    board[62] = BLACK_KNIGHT
    # bishops
    board[2] = WHITE_BISHOP
    board[5] = WHITE_BISHOP
    board[58] = BLACK_BISHOP
    board[61] = BLACK_BISHOP
    # queens
    board[4] = WHITE_QUEEN
    board[60] = BLACK_QUEEN
    # kings
    board[3] = WHITE_KING
    board[59] = BLACK_KING
    return board

def pawn_deltas (board, index):
    piece = board[index]
    allegiance = piece_allegiance(piece)

    # White allegiance initial values
    forward, forward_2 = 8, 16
    diag_r, diag_l = 7, 9

    if allegiance == BLACK_KING:
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
    if forward in range(64) and board[forward] == EMPTY:
        available.append(forward)
        if (8 <= index <= 15) or (48 <= index <= 55):
            if forward_2 in range(64) and board[forward_2] == EMPTY:
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
        while new_index in range(64) and board[new_index] == EMPTY:
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
            if board[new_index] == EMPTY or pieces_are_enemies(board[index], board[new_index]):
                moves.append(new_index)
    return moves

def rook_moves (board, index):
    perpendicular_deltas = (-1, 1, -8, 8)
    moves = []
    for di in perpendicular_deltas:
        new_index = index + di
        while new_index in range(64) and board[new_index] == EMPTY:
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
            if board[new_index] == EMPTY or pieces_are_enemies(board[index], board[new_index]):
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
    if role == WHITE_PAWN:
        return pawn_moves(board, index)
    elif role == WHITE_BISHOP:
        return bishop_moves(board, index)
    elif role == WHITE_KNIGHT:
        return knight_moves(board, index)
    elif role == WHITE_ROOK:
        return rook_moves(board, index)
    elif role == WHITE_QUEEN:
        return queen_moves(board, index)
    elif role == WHITE_KING:
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
    '''[WHITE_KING | BLACK_KING] -> [True | False]'''
    king_index = find_piece(board, king)
    return piece_is_threatened(board, king_index)

def piece_is_threatened (board, index):
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

def piece_name_allegiance (allegiance) -> str:
    if allegiance == WHITE_KING:
        return 'white'
    else:
        return 'black'

def piece_name_role (role) -> str:
    if role == WHITE_PAWN:
        return 'pawn'
    elif role == WHITE_BISHOP:
        return 'bishop'
    elif role == WHITE_KNIGHT:
        return 'knight'
    elif role == WHITE_ROOK:
        return 'rook'
    elif role == WHITE_QUEEN:
        return 'queen'
    elif role == WHITE_KING:
        return 'king'
    else:
        return ValueError('invalid chess piece role')

def piece_name (piece) -> str:
    '''Name a piece in English'''
    allegiance = piece_name_allegiance(piece_allegiance(piece))
    role = piece_name_role(piece_role(piece))
    return allegiance + ' ' + role

def piece_describe (board, index) -> str:
    '''Describe a piece on the board in English'''
    piece = board[index]
    coord = index_name(index)
    if piece == EMPTY:
        return '%s is EMPTY' %(coord)
    else:
        name = piece_name(piece)
        moves = ' or '.join([index_name(x) for x in piece_moves(board, index)])
        if moves:
            return 'the %s at %s can move to %s' %(name, coord, moves)
        else:
            return 'the %s at %s can not move' %(name, coord)

