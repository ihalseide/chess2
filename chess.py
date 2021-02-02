# This file contains the main code and logic behind the game of Chess

# I use these line breaks to avoid some mistakes, since it is important that these constant numbers are correct
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

def get_current_team (turn_number):
    if turn_number % 2 == 0:
        return WHITE_KING
    else:
        return BLACK_KING

def pieces_are_enemies (p1, p2):
    p1_team = piece_team(p1)
    p2_team = piece_team(p2)
    if p1_team is None or p2_team is None:
        return False 
    else:
        return not (p1_team == p2_team)

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
    team = name_team(piece_team(piece))
    role = name_role(piece_role(piece))
    if team and role:
        return team+' '+role

def piece_role (piece):
    '''Return the piece's role by converting it to the white team'''
    if WHITE_PAWN <= piece <= BLACK_KING:
        if piece > WHITE_KING:
            piece -= WHITE_KING
        return piece
    else:
        return None

def piece_team (piece):
    '''Return white king or black king'''
    if WHITE_PAWN <= piece <= BLACK_KING:
        if WHITE_PAWN <= piece <= WHITE_KING:
            return WHITE_KING
        else:
            return BLACK_KING
    else:
        return None

def role_as_team (role, team):
    if team == WHITE_KING:
        return role
    elif team == BLACK_KING:
        return role + 6
    else:
        return None

class Board:
    standard = [
            BLACK_ROOK, BLACK_KNIGHT, BLACK_BISHOP, BLACK_QUEEN, BLACK_KING, BLACK_BISHOP, BLACK_KNIGHT, BLACK_ROOK,
            BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN,
            EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
            EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
            EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
            EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
            WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN,
            WHITE_ROOK, WHITE_KNIGHT, WHITE_BISHOP, WHITE_QUEEN, WHITE_KING, WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK,
            ]

    def __init__ (self, pieces=None, has_moved=None, rows=8, columns=8, turn=0):
        self.rows = rows
        self.columns = columns
        self.squares = self.rows * self.columns
        self.pieces = pieces or [x for x in self.standard]
        self.has_moved = has_moved or [False for x in range(self.squares)]
        self.turn = turn

    def get_winner (self):
        white_can_move = False
        black_can_move = False
        for piece, moves in self.team_moves(WHITE_KING).items():
            if len(moves):
                white_can_move = True
                break
        for piece, moves in self.team_moves(BLACK_KING).items():
            if len(moves):
                black_can_move = True
                break
        if not white_can_move:
            return BLACK_KING
        elif not black_can_move:
            return WHITE_KING
        else:
            return None

    def in_range (self, row, col):
        return row in range(0, self.rows) and col in range(self.columns)

    def rowcol_to_index (self, row, col):
        if self.in_range(row, col):
            return (row * self.columns) + col
        else:
            return None

    def index_to_rowcol (self, index):
        if index in range(self.squares):
            row = index // 8
            col = index % 8
            return (row, col)
        else:
            return None

    def set (self, row, col, piece):
        i = self.rowcol_to_index(row, col)
        if i is not None:
            self.pieces[i] = piece
        else:
            raise ValueError('invalid row or column')

    def get (self, row, col):
        i = self.rowcol_to_index(row, col)
        if i is not None:
            return self.pieces[i]
        else:
            raise ValueError('invalid row or column')

    def copy (self):
        new = Board()
        for index, piece in enumerate(self.pieces):
            new.pieces[index] = piece
        return new

    def piece_is_threatened (self, row, col, empty_team=None):
        threats = self.piece_threat_list(row, col, empty_team)
        return len(threats) > 0

    def piece_threat_list (self, row, col, empty_team=None):
        '''Return a list of enemy pieces that threaten the given piece'''
        piece = self.get(row, col)
        result = []
        for i in range(self.squares):
            other_row, other_col = self.index_to_rowcol(i)
            if self.piece_is_threatened_by(row, col, other_row, other_col, empty_team):
                result.append((other_row, other_col))
        return result

    def piece_is_threatened_by (self, row, col, by_row, by_col, empty_team=None):
        piece = self.get(row, col)
        other = self.get(by_row, by_col)
        team_empty_threat = (empty_team is not None) and (other != EMPTY) and piece_team(other) != empty_team
        if pieces_are_enemies(piece, other) or team_empty_threat:
            return (row, col) in self.piece_moves(by_row, by_col)
        else:
            return False

    def empty_or_enemy (self, piece, row, col):
        return (self.get(row, col) == EMPTY) or pieces_are_enemies(piece, self.get(row, col))

    def piece_moves (self, row, col) -> list:
        role = piece_role(self.get(row, col))
        if role == WHITE_PAWN:
            return self.pawn_moves(row, col)
        elif role == WHITE_BISHOP:
            return self.bishop_moves(row, col)
        elif role == WHITE_KNIGHT:
            return self.knight_moves(row, col)
        elif role == WHITE_ROOK:
            return self.rook_moves(row, col)
        elif role == WHITE_QUEEN:
            return self.queen_moves(row, col)
        elif role == WHITE_KING:
            return self.king_moves(row, col)
        else:
            return []

    def pawn_moves (self, row, col):
        moves = []
        piece = self.get(row, col)
        forward, forward_2, diag_r, diag_l = pawn_plus_deltas(row, col, piece_team(piece))
        # Moving forward 1 and 2 spaces
        if self.in_range(*forward) and self.get(*forward) == EMPTY:
            moves.append(forward)
            # First move can be 2 spaces too
            if row in (1, 6) and self.in_range(*forward_2) and self.get(*forward_2) == EMPTY:
                moves.append(forward_2)
        # Capturing diagonals
        for diag in (diag_r, diag_l):
            if self.in_range(*diag) and pieces_are_enemies(piece, self.get(*diag)):
                moves.append(diag)
        return moves

    def bishop_moves (self, row, col):
        moves = []
        for drow in (-1, 1):
            for dcol in (-1, 1):
                new_row = row + drow
                new_col = col + dcol
                while self.in_range(new_row, new_col) and self.get(new_row, new_col) == EMPTY:
                    moves.append((new_row, new_col))
                    new_row += drow
                    new_col += dcol
                # The very last square traversed can be a capture
                piece = self.get(row, col)
                if self.in_range(new_row, new_col) and pieces_are_enemies(piece, self.get(new_row, new_col)):
                    moves.append((new_row, new_col))
        return moves

    def knight_moves (self, row, col):
        leaping_deltas = [(-1, -2), (1, -2), (-1, 2), (1, 2), (2, -1), (2, 1), (-2, -1), (-2, 1)]
        moves = []
        piece = self.get(row, col)
        for drow, dcol in leaping_deltas:
            new_row = row + drow
            new_col = col + dcol
            if self.in_range(new_row, new_col) and self.empty_or_enemy(piece, new_row, new_col):
                moves.append((new_row, new_col))
        return moves

    def rook_moves (self, row, col):
        moves = []
        for drow, dcol in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row = row + drow
            new_col = col + dcol
            while self.in_range(new_row, new_col) and self.get(new_row, new_col) == EMPTY:
                moves.append((new_row, new_col))
                new_row += drow
                new_col += dcol
            # The very last square traversed can be a capture
            piece = self.get(row, col)
            if self.in_range(new_row, new_col) and self.empty_or_enemy(piece, new_row, new_col):
                moves.append((new_row, new_col))
        return moves

    def queen_moves (self, row, col):
        rook = self.rook_moves(row, col)
        bishop = self.bishop_moves(row, col)
        return rook + bishop

    def king_moves (self, row, col):
        moves = []
        piece = self.get(row, col)
        for drow in (-1, 0, 1):
            for dcol in (-1, 0, 1):
                if drow == 0 and dcol == 0:
                    continue
                new_row = row + drow
                new_col = col + dcol
                if self.in_range(new_row, new_col) and self.empty_or_enemy(piece, new_row, new_col):
                    moves.append((new_row, new_col))
        return moves

    def white_pieces (self):
        for x in self.team_pieces(WHITE_KING):
            yield x

    def black_pieces (self):
        for x in self.team_pieces(BLACK_KING):
            yield x

    def team_pieces (self, team):
        '''Generator for all pieces that have the given team.
        YIELDS (piece index, piece id)'''
        for index, piece in enumerate(self.pieces):
            if piece_team(piece) == team:
                yield self.index_to_rowcol(index), piece

    def team_moves (self, team):
        '''Get all moves that a team can make, including not allowing
        moves that put the King in Check'''
        all_moves = dict()
        for (row, col), piece in self.team_pieces(team):
            no_threat = lambda to_rowcol: not self.move_would_threaten_king(row, col, *to_rowcol, team)
            moves = filter(no_threat, self.piece_moves(row, col))
            all_moves[(row, col)] = list(moves)
        return all_moves

    def move_would_threaten_king (self, from_row, from_col, to_row, to_col, team):
        simulation_board = self.copy()
        simulation_board.move(from_row, from_col, to_row, to_col)
        return simulation_board.king_is_in_check(team)

    def white_moves (self):
        return self.team_moves(WHITE_KING)

    def black_moves (self):
        return self.team_moves(BLACK_KING)

    def find_piece (self, piece):
        for i, p in enumerate(self.pieces):
            if p == piece:
                return self.index_to_rowcol(i)

    def find_pieces (self, piece):
        found = []
        for i, p in enumerate(self.pieces):
            if p == piece:
                found.append(self.index_to_rowcol(i))
        return tuple(found)

    def king_is_in_check (self, king):
        king_row, king_col = self.find_piece(king)
        return self.piece_is_threatened(king_row, king_col)

    def move (self, from_row, from_col, to_row, to_col):
        i = self.rowcol_to_index(from_row, from_col)
        self.has_moved[i] = True
        self.set(to_row, to_col, self.get(from_row, from_col))
        self.set(from_row, from_col, EMPTY)

    def is_promotable (self, row, column):
        piece = self.get(row, column) 
        if piece != EMPTY:
            team = piece_team(piece)
            role = piece_role(piece)
            if role == WHITE_PAWN:
                if team == WHITE_KING:
                    return row == 0
                elif team == BLACK_KING:
                    return row == 7
            else:
                return False
        else:
            return False

    def can_promote (self, row, column, to_role):
        valid_role = to_role in (WHITE_QUEEN, WHITE_BISHOP, WHITE_ROOK, WHITE_KNIGHT)
        return self.is_promotable(row, column) and valid_role

    def promote (self, team, row, column, to_role):
        # For when you want to promote a pawn
        self.set(row, column, role_as_team(to_role, team))

    def is_king_moved (self, king):
        if king == WHITE_KING:
            king_i = self.rowcol_to_index(7, 4)
        elif king == BLACK_KING:
            king_i = self.rowcol_to_index(0, 4)
        else:
            raise ValueError(str(king))
        return self.has_moved[king_i]

    def can_queenside_castle (self, king):
        assert king in (BLACK_KING, WHITE_KING)
        if king == WHITE_KING:
            rook_i = self.rowcol_to_index(7, 0)
            empty1_i = (7, 1)
            empty2_i = (7, 2)
            empty3_i = (7, 3)
        elif king == BLACK_KING:
            rook_i = self.rowcol_to_index(0, 0)
            empty1_i = (0, 1)
            empty2_i = (0, 2)
            empty3_i = (0, 3)
        empty1 = self.get(*empty1_i)
        empty2 = self.get(*empty2_i)
        empty3 = self.get(*empty3_i)
        king_moved = self.is_king_moved(king)
        rook_moved = self.has_moved[rook_i]
        is_clear = (empty1 == EMPTY) and (empty2 == EMPTY) and (empty3 == EMPTY)
        in_check = self.king_is_in_check(king)
        will_check = self.piece_is_threatened(*empty3_i, empty_team=king) or self.piece_is_threatened(*empty2_i, empty_team=king)
        return (not in_check) and (not will_check) and is_clear and (not king_moved) and (not rook_moved)

    def move_queenside_castle (self, king):
        assert king in (WHITE_KING, BLACK_KING)
        row, king_col = self.find_piece(king)
        rook_col = 0
        self.move(row, king_col, row, 2)
        self.move(row, rook_col, row, 3)

    def can_kingside_castle (self, king):
        assert king in (WHITE_KING, BLACK_KING) 
        if king == WHITE_KING:
            rook_i = self.rowcol_to_index(7, 7)
            empty1_i = (7, 6)
            empty2_i = (7, 5)
        elif king == BLACK_KING:
            rook_i = self.rowcol_to_index(0, 7)
            empty1_i = (0, 6)
            empty2_i = (0, 5)

        empty1 = self.get(*empty1_i)
        empty2 = self.get(*empty2_i)
        king_moved = self.is_king_moved(king)
        rook_moved = self.has_moved[rook_i]
        is_clear = (empty1 == EMPTY) and (empty2 == EMPTY)
        in_check = self.king_is_in_check(king)
        will_check = self.piece_is_threatened(*empty1_i, empty_team=king) or self.piece_is_threatened(*empty2_i, empty_team=king)
        return (not in_check) and (not will_check) and is_clear and (not king_moved) and (not rook_moved)

    def move_kingside_castle (self, king):
        assert king in (WHITE_KING, BLACK_KING)
        row, king_col = self.find_piece(king)
        rook_col = 7
        self.move(row, king_col, row, 6)
        self.move(row, rook_col, row, 5)

    def is_legal_move (self, team, from_row, from_col, to_row, to_col):
        # TODO: pre-calculate legal moves every time a real move is made
        # This calculates all moves available currently
        all_moves = self.team_moves(team)
        the_piece_moves = all_moves.get((from_row, from_col))
        if the_piece_moves:
            return (to_row, to_col) in the_piece_moves
        else:
            return False

def is_promotable_role (role):
    return role in (WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK, WHITE_QUEEN)

def pawn_deltas (team):
    # White team initial values
    # (delta row, delta column)
    forward = [1, 0]
    forward_2 = [2, 0]
    diag_r = [1, 1]
    diag_l = [1, -1]
    if team == WHITE_KING:
        forward[0] *= -1
        forward_2[0] *= -1
        diag_r[0] *= -1
        diag_l[0] *= -1
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

def square_is_white (row, col):
    row %= 2
    col %= 2
    return (row and col) or not (row or col) 

def name_square (row, col):
    max_rows = 8
    letter = 'ABCDEFGH'[col]
    return letter + str(max_rows - row)

