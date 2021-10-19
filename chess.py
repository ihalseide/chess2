#!/usr/bin/env python3

# This file contains the main code and logic behind the game of Chess 

# Note: The King Pieces are also used to represent the teams as a whole
# Note: EMPTY is not considered a piece
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

# Board properties
LENGTH = 8
NUM_SQUARES = 64 
QUEENS_ROOK_COL = 0
KINGS_ROOK_COL = 7
KING_COL = 4
STANDARD_BOARD = [
    BLACK_ROOK, BLACK_KNIGHT, BLACK_BISHOP, BLACK_QUEEN, BLACK_KING, BLACK_BISHOP, BLACK_KNIGHT, BLACK_ROOK,
    BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN,
    WHITE_ROOK, WHITE_KNIGHT, WHITE_BISHOP, WHITE_QUEEN, WHITE_KING, WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK,
] 


def is_piece (x):
    # EMPTY is not considered a piece
    return type(x) == int and x in range(1, 13)


def get_piece_role (piece):
    if not is_piece(piece):
        return None

    if WHITE_PAWN <= piece <= BLACK_KING:
        if piece > WHITE_KING:
            piece -= WHITE_KING
        return piece


def get_piece_team (piece):
    if not is_piece(piece):
        return None

    # KINGs represent their teams
    if WHITE_PAWN <= piece <= WHITE_KING:
        return WHITE_KING
    else:
        return BLACK_KING


def is_promotable_piece (piece):
    # Return whether a pawn can promote to this role
    role = get_piece_role(piece)
    return role in (WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK, WHITE_QUEEN)


def get_en_passant_row (team):
    team = get_piece_team(team)
    if team == WHITE_KING:
        return 3
    elif team == BLACK_KING:
        return 4


def get_pawn_direction (team):
    team = get_piece_team(team)
    if team == WHITE_KING:
        return -1
    elif team == BLACK_KING:
        return 1


def _pawn_deltas (team):
    dir_ = get_pawn_direction(team)

    # these values are [Δrow, Δcolumn]
    forward =   [dir_,     0]
    forward_2 = [2 * dir_, 0]
    diag_r =    [dir_,     1]
    diag_l =    [dir_,    -1]

    return forward, forward_2, diag_r, diag_l


def _pawn_plus_deltas (row, col, team):
    deltas = list(_pawn_deltas(team))
    for i, d in enumerate(deltas):
        d[0] += row
        d[1] += col
        deltas[i] = tuple(deltas[i])
    return tuple(deltas)


def in_board_range (row, col):
    return row in range(LENGTH) and col in range(LENGTH)


def rowcol_to_index (row, col):
    if in_board_range(row, col):
        return (row * LENGTH) + col


def index_to_rowcol (index):
    if index in range(NUM_SQUARES):
        row = index // LENGTH
        col = index % LENGTH
        return (row, col)


def pieces_are_enemies (piece1, piece2):
    team1 = get_piece_team(piece1)
    team2 = get_piece_team(piece2)
    return team1 != team2


def name_team (team) -> str:
    if not is_piece(team): 
        raise ValueError('not a piece')

    if team == WHITE_KING:
        return 'white'
    elif team == BLACK_KING:
        return 'black'
    else:
        assert False, "Unreachable"


def name_role (role) -> str:
    if not is_piece(role): 
        raise ValueError('not a piece')

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
        assert False, "Unreachable"


def name_piece (piece) -> str:
    team = name_team(get_piece_team(piece))
    role = name_role(get_piece_role(piece))
    return ' '.join((str(team), str(role),))


def role_as_team (role, team):
    if not is_piece(role) or not is_piece(team):
        raise ValueError('arguments must be pieces')

    if team == WHITE_KING:
        return role
    elif team == BLACK_KING:
        return role + 6


def get_king_row (piece):
    king = get_piece_team(piece)
    if king == WHITE_KING:
        return 7
    elif king == BLACK_KING:
        return 0 


def get_enemy_team (team):
    if team == WHITE_KING:
        return BLACK_KING
    elif team == BLACK_KING:
        return WHITE_KING


def get_rook_castle_cols (king_move_to_col): 
    from_col_rook = 7 if (king_move_to_col == 6) else 0
    to_col_rook = 5 if (king_move_to_col == 6) else 3
    return from_col_rook, to_col_rook 


def is_on_board (row, col):
    return row in range(LENGTH) and col in range(LENGTH)


class Game:

    def __init__ (self, pieces=None, history=None, move_num=0):
        # These lists should be a COPY of the prototypes so that they don't modify the input
        self.pieces = pieces.copy() if pieces else STANDARD_BOARD.copy()
        self.history = history.copy() if history else []
        self.move_num = move_num

        # Setup the king locations
        self.white_king_col = self.white_king_row = None
        self.black_king_col = self.black_king_row = None
        for row in range(LENGTH):
            if (self.black_king_col is not None) and (self.white_king_col is not None):
                assert self.black_king_row is not None
                assert self.white_king_row is not None
                break

            for col in range(LENGTH):
                if self.get(row, col) == WHITE_KING:
                    self.white_king_col = col
                    self.white_king_row = row

                elif self.get(row, col) == BLACK_KING:
                    self.black_king_col = col
                    self.black_king_row = row


    def get_current_team (self):
        return WHITE_KING if (self.move_num % 2 == 0) else BLACK_KING


    def set (self, row, col, piece):
        if not (is_piece(piece) or piece == EMPTY):
            raise ValueError('invalid piece: %s' % repr(piece))

        i = rowcol_to_index(row, col)
        if i is None:
            raise ValueError('invalid row or column: %s, %s' % (repr(row), repr(col)))

        self.pieces[i] = piece

        # Keep track of the kings especially
        if piece == WHITE_KING:
            self.white_king_row = row
            self.white_king_col = col
        elif piece == BLACK_KING:
            self.black_king_row = row
            self.black_king_col = col


    def get_i (self, index):
        return self.pieces[index]


    def get (self, row, col):
        i = rowcol_to_index(row, col)
        if i is None:
            raise ValueError('invalid row or column: %s, %s' % (repr(row), repr(col)))
        return self.get_i(i)


    def copy (self):
        return Game(self.pieces, self.history, self.move_num)


    def square_is_threatened (self, team, row, col):
        for other_row in range(LENGTH):
            for other_col in range(LENGTH):
                if self.square_is_threatened_by(team, row, col, other_row, other_col):
                    return True
        return False


    def square_is_threatened_by (self, team, row, col, by_row, by_col):
        team = get_piece_team(team)
        other_team = get_piece_team(self.get(by_row, by_col))
        if team == other_team:
            return False

        for e_row, e_col in self.get_piece_moves(by_row, by_col):
            if e_row == row and e_col == col:
                return True

        return False


    def empty_or_enemy (self, team, row, col):
        team = get_piece_team(team)
        piece = self.get(row, col)
        return (piece == EMPTY) or pieces_are_enemies(team, piece)


    def get_piece_moves (self, row, col, ignore_row=None, ignore_col=None):
        # ignore_row and ignore_col are for checking if a piece can threaten the king
        # if a certain other piece is ignored
        role = get_piece_role(self.get(row, col))
        if role is None:
            return []

        if role == WHITE_PAWN:
            move_func = self.get_pawn_moves_all
        elif role == WHITE_BISHOP:
            move_func =  self.get_bishop_moves
        elif role == WHITE_KNIGHT:
            move_func =  self.get_knight_moves
        elif role == WHITE_ROOK:
            move_func =  self.get_rook_moves
        elif role == WHITE_QUEEN:
            move_func =  self.get_queen_moves
        elif role == WHITE_KING:
            move_func =  self.get_king_moves_all

        if ignore_row is not None:
            return move_func(row, col, ignore_row, ignore_col)
        else:
            return move_func(row, col)


    def get_legal_piece_moves (self, row, col):
        team = get_piece_team(self.get(row, col))
        for to_row, to_col in self.get_piece_moves(row, col):
            if self._is_legal_move(team, row, col, to_row, to_col):
                yield to_row, to_col 

    
    def is_empty_or_ignore (self, row, col, ignore_row, ignore_col):
        if ignore_row is not None and ignore_col is not None:
            return (self.get(row, col) == EMPTY) or (row == ignore_row and col == ignore_col)
        return self.get(row, col) == EMPTY


    def get_pawn_moves (self, row, col, ignore_row=None, ignore_col=None):
        moves = []
        team = get_piece_team(self.get(row, col))
        forward, forward_2, diag_r, diag_l = _pawn_plus_deltas(row, col, team)
        # Moving forward 1 and 2 spaces
        if in_board_range(*forward) and self.is_empty_or_ignore(*forward, ignore_row, ignore_col):
            moves.append(forward)
            # First move can be 2 spaces too
            if row in (1, 6) and in_board_range(*forward_2) and self.is_empty_or_ignore(*forward_2, ignore_row, ignore_col):
                moves.append(forward_2)
        # Capturing diagonals
        for diag_row, diag_col in (diag_r, diag_l):
            if in_board_range(diag_row, diag_col) and pieces_are_enemies(team, self.get(diag_row, diag_col)):
                moves.append((diag_row, diag_col))
        return moves


    def get_pawn_moves_all (self, row, col, ignore_row=None, ignore_col=None):
        moves = self.get_pawn_moves(row, col, ignore_row, ignore_col)
        team = get_piece_team(self.get(row, col))

        if row == get_en_passant_row(team):
            # This list slice of the history the unnecessary data: (target, is_en_passant, is_castling)
            last_r1, last_c1, last_r2, last_c2 = self.history[-1][:4]

            last_piece = self.get(last_r2, last_c2)
            if get_piece_role(last_piece) == WHITE_PAWN:
                last_change_row = abs(last_r2 - last_r1)
                if last_change_row == 2:
                    d_col = last_c1 - col
                    on_adjacent_column = abs(d_col) == 1
                    if on_adjacent_column:
                        next_row = row + get_pawn_direction(team)
                        next_col = col + d_col
                        moves.append((next_row, next_col))

        return moves


    def get_bishop_moves (self, row, col, ignore_row=None, ignore_col=None):
        moves = []
        for drow in (-1, 1):
            for dcol in (-1, 1):
                new_row = row + drow
                new_col = col + dcol
                # Slide through empty squares
                while in_board_range(new_row, new_col) and self.is_empty_or_ignore(new_row, new_col, ignore_row, ignore_col):
                    moves.append((new_row, new_col))
                    new_row += drow
                    new_col += dcol
                # The very last square traversed can be a capture
                piece = self.get(row, col)
                if in_board_range(new_row, new_col) and pieces_are_enemies(piece, self.get(new_row, new_col)):
                    moves.append((new_row, new_col))
        return moves


    def get_knight_moves (self, row, col, ignore_row=None, ignore_col=None):
        moves = []
        piece = self.get(row, col)

        for drow, dcol in [(-1, -2), (1, -2), (-1, 2), (1, 2), (2, -1), (2, 1), (-2, -1), (-2, 1)]:
            new_row = row + drow
            new_col = col + dcol
            if in_board_range(new_row, new_col) and self.empty_or_enemy(piece, new_row, new_col):
                moves.append((new_row, new_col))

        return moves


    def get_rook_moves (self, row, col, ignore_row=None, ignore_col=None):
        moves = []

        for drow, dcol in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row = row + drow
            new_col = col + dcol
            while in_board_range(new_row, new_col) and self.is_empty_or_ignore(new_row, new_col, ignore_row, ignore_col):
                moves.append((new_row, new_col))
                new_row += drow
                new_col += dcol
            # The very last square traversed can be a capture
            piece = self.get(row, col)
            if in_board_range(new_row, new_col) and self.empty_or_enemy(piece, new_row, new_col):
                moves.append((new_row, new_col))

        return moves


    def get_queen_moves (self, row, col, ignore_row=None, ignore_col=None):
        rook = self.get_rook_moves(row, col, ignore_row, ignore_col)
        bishop = self.get_bishop_moves(row, col, ignore_row, ignore_col)
        return rook + bishop


    def get_king_moves (self, row, col, ignore_row=None, ignore_col=None):
        moves = []
        piece = self.get(row, col)
        for drow in (-1, 0, 1):
            for dcol in (-1, 0, 1):
                if drow == 0 and dcol == 0:
                    continue
                new_row = row + drow
                new_col = col + dcol
                if in_board_range(new_row, new_col) and self.empty_or_enemy(piece, new_row, new_col):
                    moves.append((new_row, new_col))
        return moves


    def get_king_moves_all (self, row, col, ignore_row=None, ignore_col=None):
        moves = self.get_king_moves(row, col)

        if self.can_castle_queenside(row, col):
            moves.append((row, QUEENS_ROOK_COL + 2))

        if self.can_castle_kingside(row, col):
            moves.append((row, KINGS_ROOK_COL - 1))

        return moves


    def get_team_pieces (self, team):
        for index, piece in enumerate(self.pieces):
            if get_piece_team(piece) == team:
                row, col = index_to_rowcol(index)
                yield (row, col, piece)


    def get_team_moves (self, team):
        team = get_piece_team(team)
        for row, col, piece in self.get_team_pieces(team):
            piece_moves = self.get_piece_moves(row, col)
            for to_row, to_col in piece_moves:
                yield (row, col, to_row, to_col)


    def get_legal_team_moves (self, team):
        for move in self.get_team_moves(team):
            if self._is_legal_move(team, *move):
                yield move


    def get_current_moves (self):
        return self.get_team_moves(self.get_current_team())


    def get_current_legal_moves (self):
        return self.get_legal_team_moves(self.get_current_team())


    def move (self, from_row, from_col, to_row, to_col):
        piece = self.get(from_row, from_col)
        self.set(to_row, to_col, piece)
        self.set(from_row, from_col, EMPTY)


    def make_move (self, from_row, from_col, to_row, to_col):
        # Check for special moves
        is_castling = is_en_passant = False
        if self.move_is_castling(from_row, from_col, to_row, to_col): 
            is_castling = True
            self.move_finish_castling(from_row, from_col, to_row, to_col)
        elif self.move_is_en_passant(from_row, from_col, to_row, to_col):
            is_en_passant = True
            self.move_finish_en_passant(from_row, from_col, to_row, to_col)
        # Change the board with the move
        target = self.get(to_row, to_col)
        self.move(from_row, from_col, to_row, to_col)
        # Log the move
        self.history.append((from_row, from_col, to_row, to_col, target, is_castling, is_en_passant))
        # Increment counter
        self.move_num += 1


    def has_moved (self, row, col):
        for move in self.history:
            from_row, from_col = move[:2]
            if row == from_row and col == from_col:
                return True
        return False


    def undo_move (self):
        last_move = self.history.pop(-1)
        from_row, from_col, to_row, to_col, target, is_castling, is_en_passant = last_move
        self.move(to_row, to_col, from_row, from_col)
        self.set(to_row, to_col, target)
        if is_en_passant:
            # Restore the captured pawn
            captured_pawn_row = from_row
            captured_pawn_col = to_col
            captured_pawn = WHITE_PAWN if (get_piece_team(self.get(from_row, from_col)) == BLACK_KING) else BLACK_PAWN
            self.set(captured_pawn_row, captured_pawn_col, captured_pawn)
        elif is_castling:
            # Move the castle back
            rook_from_col, rook_to_col = get_rook_castle_cols(to_col)
            self.move(to_row, rook_to_col, from_row, rook_from_col)
        # Do this last because other methods could potentially rely on self's current team state
        self.move_num -= 1


    def move_is_castling (self, from_row, from_col, to_row, to_col):
        piece = self.get(from_row, from_col)
        if (get_piece_role(piece) == WHITE_KING
                and (from_row == to_row == get_king_row(piece))
                and from_col == KING_COL):
            if to_col == QUEENS_ROOK_COL + 2:
                return WHITE_QUEEN
            elif to_col == KINGS_ROOK_COL - 1:
                return WHITE_KING
        return False


    def move_finish_castling (self, from_row, from_col, to_row, to_col):
        # Move the appropriate rook next to the king
        from_col_rook, to_col_rook = get_rook_castle_cols(to_col)
        rook = self.get(from_row, from_col_rook)
        self.set(to_row, to_col_rook, rook)
        self.set(from_row, from_col_rook, EMPTY)


    def move_is_en_passant (self, from_row, from_col, to_row, to_col):
        piece = self.get(from_row, from_col)
        team = get_piece_team(piece)
        return (get_piece_role(piece) == WHITE_PAWN
                and from_col != to_col
                and from_row == get_en_passant_row(team)
                and self.get(from_row, to_col) == role_as_team(WHITE_PAWN, get_enemy_team(team)))


    def move_finish_en_passant (self, from_row, from_col, to_row, to_col):
        # Remove the captured pawn
        self.set(from_row, to_col, EMPTY)


    def is_promotable (self, row, column):
        piece = self.get(row, column) 
        return (get_piece_role(piece) == WHITE_PAWN
                and row == get_king_row(get_enemy_team(get_piece_team(piece))))


    def can_castle_queenside (self, row, col):
        king = self.get(row, col)
        return (row == get_king_row(get_piece_team(king))
                and col == KING_COL 
                and get_piece_role(king) == WHITE_KING 
                and not self.has_moved(row, KING_COL)
                and not self.has_moved(row, QUEENS_ROOK_COL)
                and (EMPTY == self.get(row, 1) == self.get(row, 2) == self.get(row, 3))
                and not self.square_is_threatened(king, row, col)
                and not self.square_is_threatened(king, row, col - 1)
                and not self.square_is_threatened(king, row, col - 2)
                and not self.square_is_threatened(king, row, col - 3))


    def can_castle_kingside (self, row, col):
        king = self.get(row, col)
        return (row == get_king_row(get_piece_team(king))
                and col == KING_COL
                and get_piece_role(king) == WHITE_KING
                and not self.has_moved(row, KING_COL)
                and not self.has_moved(row, KINGS_ROOK_COL)
                and (EMPTY == self.get(row, 5) == self.get(row, 6)) 
                and not self.square_is_threatened(king, row, col)
                and not self.square_is_threatened(king, row, col - 1)
                and not self.square_is_threatened(king, row, col - 2))


    def is_legal_move (self, team, from_row, from_col, to_row, to_col):
        piece = self.get(from_row, from_col)
        return (get_piece_team(piece) == team
                and (to_row, to_col) in self.get_piece_moves(from_row, from_col)
                and not self.move_would_threaten_king(team, from_row, from_col, to_row, to_col))

    def _is_legal_move (self, team, from_row, from_col, to_row, to_col):
        # This is an internal function called by other get_moves-like functions,
        # we don't need to check if it's in self.get_piece_moves because the moves are already
        # generated by piece movement functions
        piece = self.get(from_row, from_col)
        return (get_piece_team(piece) == team
                and not self.move_would_threaten_king(team, from_row, from_col, to_row, to_col))


    def move_would_threaten_king (self, team, from_row, from_col, to_row, to_col):
        team = get_piece_team(team)
        enemy = get_enemy_team(team)
        king_row, king_col = self.find_king(team)

        for (e_from_row, e_from_col, e_to_row, e_to_col) in self.get_team_moves(enemy):
            # King moving into check
            if king_row == e_to_row and king_col == e_to_col:
                return True

            # Moving a piece and allowing an enemy that was threatening that piece to attack king instead.
            # (kinda a discovered check)
            if e_to_row == from_row and e_to_col == from_col:
                role = get_piece_role(self.get(e_from_row, e_from_col))
                discover_moves = self.get_piece_moves(e_from_row, e_from_col)
                for e_row, e_col in discover_moves:
                    if e_row == king_row and e_col == king_col:
                        return True

        return False


    def find_king (self, king):
        king = get_piece_team(king)
        if king == WHITE_KING:
            return self.white_king_row, self.white_king_col
        elif king == BLACK_KING:
            return self.black_king_row, self.black_king_col


    def is_king_in_check (self, king):
        king = get_piece_team(king)
        row, col = self.find_king(king)
        return self.square_is_threatened(king, row, col)


    def is_game_over (self):
        return (not len(tuple(self.get_legal_team_moves(BLACK_KING)))
                or not len(tuple(self.get_legal_team_moves(WHITE_KING))))


    def get_winner (self):
        if self.is_game_over():
            if self.is_king_in_check(BLACK_KING):
                return WHITE_KING
            elif self.is_king_in_check(WHITE_KING):
                return BLACK_KING

def _test ():
    assert LENGTH * LENGTH == NUM_SQUARES
    assert len(STANDARD_BOARD) == NUM_SQUARES

    assert not is_piece(True)
    assert not is_piece(False)
    assert not is_piece(None)
    assert not is_piece(EMPTY)

    assert is_piece(WHITE_PAWN)
    assert is_piece(WHITE_BISHOP)
    assert is_piece(WHITE_KNIGHT)
    assert is_piece(WHITE_ROOK)
    assert is_piece(WHITE_QUEEN)
    assert is_piece(WHITE_KING)
    assert is_piece(BLACK_PAWN)
    assert is_piece(BLACK_BISHOP)
    assert is_piece(BLACK_KNIGHT)
    assert is_piece(BLACK_ROOK)
    assert is_piece(BLACK_QUEEN)
    assert is_piece(BLACK_KING)

    x = WHITE_KING
    assert get_enemy_team(get_enemy_team(x)) == x
    x = BLACK_KING
    assert get_enemy_team(get_enemy_team(x)) == x

    test = Game()
    assert test.white_king_col == 4
    assert test.white_king_row == 7
    assert test.black_king_col == 4
    assert test.black_king_row == 0
    assert not test.is_game_over()
    assert test.get_winner() == None
    assert test.move_num == 0
    assert len(list(test.get_team_moves(WHITE_KING))) == 20
    assert len(list(test.get_team_moves(WHITE_KING))) == 20
    assert len(list(test.get_legal_team_moves(WHITE_KING))) == 20
    assert len(list(test.get_legal_team_moves(WHITE_KING))) == 20


if __name__ == '__main__':
    _test()

