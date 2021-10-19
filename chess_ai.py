import time, random 
import chess 
from chess_ai_positions import *

def get_piece_value (piece, row, col):
    if chess.is_piece(piece):
        role = chess.get_piece_role(piece)
        is_white = chess.get_piece_team(piece) == chess.WHITE_KING
        i = chess.rowcol_to_index(row, col) 
        if role == chess.WHITE_KING:
            val = 900, (KING_EVAL_WHITE if is_white else KING_EVAL_BLACK)
        elif role == chess.WHITE_QUEEN:
            val = 90, (QUEEN_EVAL_WHITE if is_white else QUEEN_EVAL_BLACK)
        elif role == chess.WHITE_ROOK:
            val = 50, (ROOK_EVAL_WHITE if is_white else ROOK_EVAL_BLACK)
        elif role == chess.WHITE_KNIGHT:
            val = 30, (KNIGHT_EVAL_WHITE if is_white else KNIGHT_EVAL_BLACK)
        elif role == chess.WHITE_BISHOP:
            val = 30, (BISHOP_EVAL_WHITE if is_white else BISHOP_EVAL_BLACK)
        elif role == chess.WHITE_PAWN:
            val = 10, (PAWN_EVAL_WHITE if is_white else PAWN_EVAL_BLACK)
        abs_val = val[0] + val[1][i]
        return abs_val if is_white else -abs_val
    else:
        return 0

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

def ai_process (board, time_limit):
    start_time = time.time_ns()
    depth = 1
    last_time_taken = 0
    move = None
    while (time.time_ns() - start_time + last_time_taken) < time_limit:
        move = minimax_root(board, depth, is_maximizing_player=True) 
        depth += 1
        last_time_taken = time.time_ns() - start_time
    return (move, depth)

