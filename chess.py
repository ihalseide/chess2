# This file contains the main code and logic behind the game of Chess

# Use these line breaks to avoid mistakes, since it is important that these constant numbers are correct
# The kings are also used to represent the teams as a whole
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

# Board size constants for calculations
LENGTH = 8
NUM_SQUARES = LENGTH * LENGTH

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

# Standard piece locations for castling
QUEENS_ROOK_COL = 0
KINGS_ROOK_COL = 7
KING_COL = 4

# (General utility function not specifically for chess)
def list_copy (list_) -> list:
    return [x for x in list_]

class Board:

    def __init__ (self, pieces=None, history=None, move_num=0):
        # These lists should be a COPY of the prototypes so that they don't modify the input
        # lists!
        if pieces is None:
            self.pieces = list_copy(STANDARD_BOARD)
        else:
            self.pieces = list_copy(pieces) 
        self.history = list_copy(history) if history else []
        self.move_num = move_num

    def get_current_team (self):
        # Call the global function that is defined elsewhere
        return get_current_team(self.move_num)

    def set (self, row, col, piece):
        i = rowcol_to_index(row, col)
        if i is not None:
            if is_piece(piece) or piece == EMPTY:
                self.pieces[i] = piece
            else:
                raise ValueError('invalid piece')
        else:
            raise ValueError('invalid row or column')

    def get (self, row, col):
        i = rowcol_to_index(row, col)
        if i is not None:
            return self.pieces[i]
        else:
            raise ValueError('invalid row or column')

    def copy (self):
        return Board(self.pieces, self.history, self.move_num)

    def get_piece_is_threatened (self, row, col):
        team = get_piece_team(self.get(row, col))
        return self.get_square_is_threatened(team, row, col)

    def get_square_is_threatened (self, team, row, col):
        return len(self.get_square_threats(get_piece_team(team), row, col)) > 0

    def get_square_threats (self, team, row, col):
        result = []
        for other_row in range(LENGTH):
            for other_col in range(LENGTH):
                if self.get_square_is_threatened_by(team, row, col, other_row, other_col):
                    result.append((other_row, other_col))
        return result

    def get_square_is_threatened_by (self, team, row, col, by_row, by_col):
        team = get_piece_team(team)
        other_team = get_piece_team(self.get(by_row, by_col))
        return team != other_team and (row, col) in self.get_piece_moves(by_row, by_col)

    def empty_or_enemy (self, team, row, col):
        team = get_piece_team(team)
        return (self.get(row, col) == EMPTY) or pieces_are_enemies(team, self.get(row, col))

    def get_piece_moves (self, row, col) -> list:
        role = get_piece_role(self.get(row, col))
        if role:
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
            return move_func(row, col)
        else:
            return []

    def get_pawn_moves (self, row, col):
        moves = []
        piece = self.get(row, col)
        forward, forward_2, diag_r, diag_l = pawn_plus_deltas(row, col, get_piece_team(piece))
        # Moving forward 1 and 2 spaces
        if in_board_range(*forward) and self.get(*forward) == EMPTY:
            moves.append(forward)
            # First move can be 2 spaces too
            if row in (1, 6) and in_board_range(*forward_2) and self.get(*forward_2) == EMPTY:
                moves.append(forward_2)
        # Capturing diagonals
        for diag in (diag_r, diag_l):
            if in_board_range(*diag) and pieces_are_enemies(piece, self.get(*diag)):
                moves.append(diag)
        return moves

    def get_pawn_moves_all (self, row, col):
        moves = self.get_pawn_moves(row, col)
        piece = self.get(row, col)
        if row == get_en_passant_row(piece):
            # History slice ignores the unnecessary data (target, is_en_passant, is_castling)
            last_r1, last_c1, last_r2, last_c2 = self.history[-1][:4]
            last_piece = self.get(last_r2, last_c2)
            if get_piece_role(last_piece) == WHITE_PAWN:
                last_change_row = abs(last_r2 - last_r1)
                if last_change_row == 2:
                    d_col = last_c1 - col
                    on_adjacent_column = abs(d_col) == 1
                    if on_adjacent_column:
                        next_row = row + get_pawn_direction(get_piece_team(piece))
                        next_col = col + d_col
                        moves.append((next_row, next_col))
        return moves

    def get_bishop_moves (self, row, col):
        moves = []
        for drow in (-1, 1):
            for dcol in (-1, 1):
                new_row = row + drow
                new_col = col + dcol
                while in_board_range(new_row, new_col) and self.get(new_row, new_col) == EMPTY:
                    moves.append((new_row, new_col))
                    new_row += drow
                    new_col += dcol
                # The very last square traversed can be a capture
                piece = self.get(row, col)
                if in_board_range(new_row, new_col) and pieces_are_enemies(piece, self.get(new_row, new_col)):
                    moves.append((new_row, new_col))
        return moves

    def get_knight_moves (self, row, col):
        leaping_deltas = [(-1, -2), (1, -2), (-1, 2), (1, 2), (2, -1), (2, 1), (-2, -1), (-2, 1)]
        moves = []
        piece = self.get(row, col)
        for drow, dcol in leaping_deltas:
            new_row = row + drow
            new_col = col + dcol
            if in_board_range(new_row, new_col) and self.empty_or_enemy(piece, new_row, new_col):
                moves.append((new_row, new_col))
        return moves

    def get_rook_moves (self, row, col):
        moves = []
        for drow, dcol in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row = row + drow
            new_col = col + dcol
            while in_board_range(new_row, new_col) and self.get(new_row, new_col) == EMPTY:
                moves.append((new_row, new_col))
                new_row += drow
                new_col += dcol
            # The very last square traversed can be a capture
            piece = self.get(row, col)
            if in_board_range(new_row, new_col) and self.empty_or_enemy(piece, new_row, new_col):
                moves.append((new_row, new_col))
        return moves

    def get_queen_moves (self, row, col):
        rook = self.get_rook_moves(row, col)
        bishop = self.get_bishop_moves(row, col)
        return rook + bishop

    def get_king_moves (self, row, col):
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

    def get_king_moves_all (self, row, col):
        moves = self.get_king_moves(row, col)
        if self.can_castle_queenside(row, col):
            moves.append((row, QUEENS_ROOK_COL + 2))
        if self.can_castle_kingside(row, col):
            moves.append((row, KINGS_ROOK_COL - 1))
        return moves

    def get_team_pieces (self, team):
        '''Generator for all pieces that have the given team.
        YIELDS (piece index, piece id)'''
        for index, piece in enumerate(self.pieces):
            if get_piece_team(piece) == team:
                yield (*index_to_rowcol(index), piece)

    def get_team_moves (self, team) -> list:
        '''Get all moves that a team can legally make
        Returns a list of 4-tuples: [(from_row, from_col, to_row, to_col), ...]
        '''
        moves = []
        for row, col, piece in self.get_team_pieces(team):
            piece_moves = self.get_piece_moves(row, col)
            for to_row, to_col in piece_moves:
                if self.is_legal_move(team, row, col, to_row, to_col):
                    moves.append((row, col, to_row, to_col))
        return moves

    def get_current_moves (self):
        return self.get_team_moves(self.get_current_team())

    def find_piece (self, piece):
        '''Find the first location of a given piece type'''
        for i, p in enumerate(self.pieces):
            if p == piece:
                return index_to_rowcol(i)

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
        row, col = get_en_passant_capture(from_row, from_col, to_row, to_col)
        self.set(row, col, EMPTY)

    def is_promotable (self, row, column):
        piece = self.get(row, column) 
        return (get_piece_role(piece) == WHITE_PAWN
                and row == get_king_row(get_enemy_team(get_piece_team(piece))))

    def can_castle_queenside (self, row, col):
        king = self.get(row, col)
        return (get_piece_role(king) == WHITE_KING
                and not self.has_moved(row, KING_COL)
                and not self.has_moved(row, QUEENS_ROOK_COL)
                and (EMPTY == self.get(row, 1) == self.get(row, 2) == self.get(row, 3))
                and not self.get_piece_is_threatened(row, col))

    def can_castle_kingside (self, row, col):
        king = self.get(row, col)
        # Checking if the king is in check should be done elsewhere
        return (get_piece_role(king) == WHITE_KING
                and not self.has_moved(row, KING_COL)
                and not self.has_moved(row, KINGS_ROOK_COL)
                and (EMPTY == self.get(row, 5) == self.get(row, 6)))

    def is_legal_move (self, team, from_row, from_col, to_row, to_col):
        piece = self.get(from_row, from_col)
        return (get_piece_team(piece) == team
                and (to_row, to_col) in self.get_piece_moves(from_row, from_col)
                and not self.move_would_threaten_king(team, from_row, from_col, to_row, to_col))

    def move_would_threaten_king (self, team, from_row, from_col, to_row, to_col):
        team = get_piece_team(team)
        sim = self.copy()
        sim.make_move(from_row, from_col, to_row, to_col)
        if sim.find_piece(team):
            return sim.is_king_in_check(team)
        else:
            return True

    def is_king_in_check (self, king):
        king = get_piece_team(king)
        row, col = self.find_piece(king)
        return self.get_square_is_threatened(king, row, col)

    def can_team_move (self, king):
        moves = self.get_team_moves(get_piece_team(king))
        return len(moves) > 0

    def is_king_in_checkmate (self, king):
        return self.is_king_in_check(king) and not self.can_team_move(king)

    def is_king_in_stalemate (self, king):
        return not self.is_king_in_check(king) and not self.can_team_move(king)

    def is_game_over (self):
        return ((not self.can_team_move(BLACK_KING))
                or (not self.can_team_move(WHITE_KING)))

    def get_winner (self):
        if self.is_king_in_checkmate(BLACK_KING):
            return WHITE_KING
        elif self.is_king_in_checkmate(WHITE_KING):
            return BLACK_KING

def is_promotable_role (role):
    return role in (WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK, WHITE_QUEEN)

def get_en_passant_row (team):
    return 3 if (get_piece_team(team) == WHITE_KING) else 4

def get_pawn_direction (team):
    return -1 if (team == WHITE_KING) else 1

def pawn_deltas (team):
    dir_ = get_pawn_direction(team)
    # (delta row, delta column)
    forward =   [dir_, 0]
    forward_2 = [2 * dir_, 0]
    diag_r =    [dir_, 1]
    diag_l =    [dir_, -1]
    return forward, forward_2, diag_r, diag_l

def pawn_plus_deltas (row, col, team):
    deltas = list(pawn_deltas(team))
    for i, d in enumerate(deltas):
        d[0] += row
        d[1] += col
        deltas[i] = tuple(deltas[i])
    return tuple(deltas)

def standard_board ():
    board = Board()
    return board

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

def get_current_team (turn_number):
    return WHITE_KING if (turn_number % 2 == 0) else BLACK_KING

def pieces_are_enemies (piece1, piece2):
    team1 = get_piece_team(piece1)
    team2 = get_piece_team(piece2)
    return is_piece(team1) and is_piece(team2) and team1 != team2

def name_team (team) -> str:
    if team == WHITE_KING:
        return 'white'
    elif team == BLACK_KING:
        return 'black'

def name_role (role) -> str:
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

def name_piece (piece) -> str:
    '''Name a piece in English'''
    team = name_team(get_piece_team(piece))
    role = name_role(get_piece_role(piece))
    if team and role:
        return team+' '+role

def get_piece_role (piece):
    '''Return the piece's role by converting it to the white team'''
    if WHITE_PAWN <= piece <= BLACK_KING:
        if piece > WHITE_KING:
            piece -= WHITE_KING
        return piece

def get_piece_team (piece):
    '''Return white king or black king'''
    if WHITE_PAWN <= piece <= BLACK_KING:
        if WHITE_PAWN <= piece <= WHITE_KING:
            return WHITE_KING
        else:
            return BLACK_KING

def is_promote_piece (piece):
    role = get_piece_role(piece)
    return role in (WHITE_QUEEN, WHITE_BISHOP, WHITE_ROOK, WHITE_KNIGHT)

def role_as_team (role, team):
    if team == WHITE_KING:
        return role
    elif team == BLACK_KING:
        return role + 6

def get_king_row (piece):
    king = get_piece_team(piece)
    assert king is not None
    if king == WHITE_KING:
        return 7
    elif king == BLACK_KING:
        return 0 

def get_enemy_team (team):
    if team == WHITE_KING:
        return BLACK_KING
    elif team == BLACK_KING:
        return WHITE_KING

def is_piece (x):
    return x in range(1, 13)

def get_en_passant_capture (from_row, from_col, to_row, to_col):
    return (from_row, to_col)

def get_rook_castle_cols (king_move_to_col): 
    from_col_rook = 7 if (king_move_to_col == 6) else 0
    to_col_rook = 5 if (king_move_to_col == 6) else 3
    return from_col_rook, to_col_rook

if __name__ == '__main__':
    assert not is_piece(False)
    assert not is_piece(None)
    assert not is_piece(EMPTY)

    assert is_piece(True)
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

    test = Board()
    moves = test.get_team_moves(WHITE_KING)
    print(len(moves))
    print(moves)
