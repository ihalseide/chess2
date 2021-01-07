#!/usr/bin/env python3

white_pawn = 'white pawn'
white_bishop = 'white bishop'
white_knight = 'white knight'
white_rook = 'white rook'
white_queen = 'white queen'
white_king = 'white king'

black_pawn = 'black pawn'
black_bishop = 'black bishop'
black_knight = 'black knight'
black_rook = 'black rook'
black_queen = 'black queen'
black_king = 'black king'

def create_board ():
    board = [None for _ in range(8 * 8)]
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

b = create_board()

def p(x):
    return x.rjust(12)

print(' '.join(p('_' if x is None else x) for x in b[0:8]))
print(' '.join(p('_' if x is None else x) for x in b[8:16]))
print(' '.join(p('_' if x is None else x) for x in b[16:24]))
print(' '.join(p('_' if x is None else x) for x in b[24:32]))
print(' '.join(p('_' if x is None else x) for x in b[32:40]))
print(' '.join(p('_' if x is None else x) for x in b[40:48]))
print(' '.join(p('_' if x is None else x) for x in b[48:56]))
print(' '.join(p('_' if x is None else x) for x in b[56:64]))
