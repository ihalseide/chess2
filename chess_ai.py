import functools
import random 
import chess 

# Value of positions for pieces on the board
PAWN_EVAL_WHITE = [
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,
        1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0,
        0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5,
        0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0,
        0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5,
        0.5,  1.0, 1.0,  -2.0, -2.0,  1.0,  1.0,  0.5,
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        ] 

PAWN_EVAL_BLACK = [
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        0.5,  1.0, 1.0,  -2.0, -2.0,  1.0,  1.0,  0.5,
        0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5,
        0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0,
        0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5,
        1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0,
        5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        ]

KNIGHT_EVAL_WHITE = [
        -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
        -4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0,
        -3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0,
        -3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0,
        -3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0,
        -3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0,
        -4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0,
        -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
        ]

KNIGHT_EVAL_BLACK = [
        -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
        -4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0,
        -3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0,
        -3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0,
        -3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0,
        -3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0,
        -4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0,
        -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
        ] 

BISHOP_EVAL_BLACK = [
        -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
        -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
        -1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0,
        -1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0,
        -1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0,
        -1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0,
        -1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0,
        -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
        ]

BISHOP_EVAL_WHITE = [
        -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
        -1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0,
        -1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0,
        -1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0,
        -1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0,
        -1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0,
        -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
        -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
        ]

ROOK_EVAL_WHITE = [
         0.0,   0.0, 0.0,  0.5,  0.5,  0.0,  0.0,  0.0,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
         0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5,
         0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        ] 

ROOK_EVAL_BLACK = [
         0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
         0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
         0.0,   0.0, 0.0,  0.5,  0.5,  0.0,  0.0,  0.0
        ] 

QUEEN_EVAL_WHITE = [
        -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
        -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
        -1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
        -0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
         0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
        -1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
        -1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0,
        -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0
        ]

QUEEN_EVAL_BLACK = [
        -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
        -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
        -1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
        -0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
         0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
        -1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
        -1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0,
        -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
        ]

KING_EVAL_WHITE = [
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0,
        -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0,
         2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0,
         2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0,
        ] 

KING_EVAL_BLACK = [
         2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0,
         2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0,
        -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0,
        -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        ] 

def get_piece_value (piece, row, col):
    if not chess.is_piece(piece):
        return 0
    else:
        role = chess.get_piece_role(piece)
        is_white = chess.get_piece_team(piece) == chess.WHITE_KING
        i = chess.rowcol_to_index(row, col)
        if not i in range(64):
            breakpoint()
        abs_val = None
        if role == chess.WHITE_KING:
            abs_val = 900 + (KING_EVAL_WHITE if is_white else KING_EVAL_BLACK)[i]
        elif role == chess.WHITE_QUEEN:
            abs_val = 90 + (QUEEN_EVAL_WHITE if is_white else QUEEN_EVAL_BLACK)[i]
        elif role == chess.WHITE_ROOK:
            abs_val = 50 + (ROOK_EVAL_WHITE if is_white else ROOK_EVAL_BLACK)[i]
        elif role == chess.WHITE_KNIGHT:
            abs_val = 30 + (KNIGHT_EVAL_WHITE if is_white else KNIGHT_EVAL_BLACK)[i]
        elif role == chess.WHITE_BISHOP:
            abs_val = 30 + (BISHOP_EVAL_WHITE if is_white else BISHOP_EVAL_BLACK)[i]
        elif role == chess.WHITE_PAWN:
            abs_val = 10 + (PAWN_EVAL_WHITE if is_white else PAWN_EVAL_BLACK)[i]
        return abs_val if is_white else -abs_val

# Evaluate a board position
def get_board_value (board):
    value = 0
    for row in range(chess.LENGTH):
        for col in range(chess.LENGTH):
            piece = board.get(row, col)
            value += get_piece_value(piece, row, col)
    return value

def minimax_root (board, depth, is_maximizing_player):
    best_value = -9999
    best_move = None 
    for i, move in enumerate(board.get_current_moves()):
        # Use a copy as to not mess up the original
        board.make_move(*move)
        value = minimax(board, depth - 1, -10_000, 10_000, not is_maximizing_player)
        board.undo_move()
        if value > best_value:
            best_value = value
            best_move = move 
    return best_move

def minimax (board, depth, alpha, beta, is_maximizing_player):
    if depth == 0:
        return -get_board_value(board)
    else:
        new_moves = board.get_current_moves()
        min_or_max = max if is_maximizing_player else min
        best_value = -9999 if is_maximizing_player else 9999
        for i, move in enumerate(new_moves):
            # Use a copy as to not mess up the original
            board.make_move(*move)
            recur = minimax(board, depth - 1, alpha, beta, not is_maximizing_player)
            best_value = min_or_max(best_value, recur)
            board.undo_move()
            if is_maximizing_player:
                alpha = max(alpha, best_value)
            else:
                beta = min(beta, best_value)
            if beta <= alpha:
                return best_value
        return best_value 

def get_move (board, team):
    if board.move_num <=1:
        depth = 2
    else:
        depth = 3
    return minimax_root(board, depth, is_maximizing_player=True)

if __name__ == '__main__':
    assert len(ROOK_EVAL_BLACK) == 64
    assert len(BISHOP_EVAL_BLACK) == 64
    assert len(QUEEN_EVAL_BLACK) == 64
    assert len(KING_EVAL_BLACK) == 64
    assert len(PAWN_EVAL_BLACK) == 64
    assert len(KNIGHT_EVAL_BLACK) == 64
    assert len(ROOK_EVAL_WHITE) == 64
    assert len(BISHOP_EVAL_WHITE) == 64
    assert len(QUEEN_EVAL_WHITE) == 64
    assert len(KING_EVAL_WHITE) == 64
    assert len(PAWN_EVAL_WHITE) == 64
    assert len(KNIGHT_EVAL_WHITE) == 64
