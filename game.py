#!/usr/bin/env python3

import pygame
import chess

CORNER_X, CORNER_Y = 64, 88
GRID_SIZE = 16
MESSAGE_X, MESSAGE_Y = 48, 72 
JAIL_START_X = 25 * 8
JAIL_END_X = 25 * 8 + 16 * 3
BLACK_JAIL_Y = 224
WHITE_JAIL_Y = 72
WIN_TEXT = [
        "you can now play as luigi",
        "free play unlocked"
        ]
LOSE_TEXT = [
        "all your base are belong to us",
        "sorry mate",
        "screams echo around you"
        ]
BACKGROUND = [
326,326,326,326,326,326,306,286,284,286,285,326,266,283,258,268,326,265,258,269,276,262,266,261,262,326,326,326,326,326,326,326,
326,326,326,326,326,326,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,326,326,326,326,326,326,
326,326,326,326,326,326,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,326,326,326,326,326,326,
326,326,326,326,326,326,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,326,326,326,326,326,326,
326,326,326,326,326,326,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,326,326,326,326,326,326,
326,326,326,326,326,326,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,326,326,326,326,326,326,
326,326,326,326,326,326,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,326,326,326,326,326,326,
326,326,326,326,326,326,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,326,326,326,326,326,326,
326,326,326,326,326,326,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,326,326,326,326,326,326,
326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,288,289,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,293,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,325,326,326,326,326,326,326,326,
326,326,326,326,326,326,298,320,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,357,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,320,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,389,326,326,326,326,326,326,326,
326,326,326,326,326,326,297,320,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,296,320,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,320,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,295,320,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,294,320,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,320,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,287,320,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,286,352,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,384,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,285,416,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,448,449,449,449,449,449,449,449,449,449,449,449,449,449,450,451,452,453,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,326,258,326,259,326,260,326,261,326,262,326,263,326,264,326,265,326,326,326,326,326,326,326,326,326,
326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,
]

class Sprite:

    def __init__(self, tile, x, y, size=1):
        self.tile = tile
        self.x = x
        self.y = y
        self.size = size

class Game:

    def __init__ (self, screen):
        self.screen = screen
        self.spritesheet = pygame.image.load('spritesheet.png')
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.init_sounds()
        self.init_chess()
        self.init_pieces()
        self.init_message()

    def init_message (self):
        self.message = None
        self.message_sprites = []
        self.update_message()
    
    def update_message (self):
        is_white = self.chess_board.get_current_team() == chess.WHITE_KING
        if self.is_promoting:
            if is_white:
                self.message = 'red # pawn promotion'
            else:
                self.message = 'blue $ pawn promotion'
        elif self.game_over:
            if is_white:
                self.message = 'blue $ won the game!'
            else:
                self.message = 'red # won the game!'
        else:
            if is_white:
                if self.chess_board.king_is_in_check(chess.WHITE_KING):
                    self.message = 'red # is in check'
                else:
                    self.message = 'red # to move'
            else:
                if self.chess_board.king_is_in_check(chess.BLACK_KING):
                    self.message = 'blue $ is in check'
                else:
                    self.message = 'blue $ to move'
        self.message_sprites = []
        for i, char in enumerate(self.message):
            tile = char_to_tile(char)
            s = Sprite(tile, MESSAGE_X + i * 8, MESSAGE_Y, 1)
            self.message_sprites.append(s)

    def init_sounds (self):
        s = pygame.mixer.Sound
        self.sounds = {
                'check': s('check.wav'),
                'checkmate': s('checkmate.wav'),
                'error': s('error.wav'),
                'move': s('move.wav'),
                'promote': s('promote.wav'),
                'can promote': s('can promote.wav'),
                'capture': s('capture.wav'),
                'castle': s('castle.wav')
                }

    def play_sound (self, name):
        sound = self.sounds[name]
        sound.play()

    def init_chess (self):
        self.chess_board = chess.Board()
        self.selected_start = None
        self.selected_end = None

    def init_pieces (self):
        self.pieces = []
        self.moving_piece = None
        self.selected_piece = None
        self.move_start = None
        self.move_end = None
        self.move_is_short_castle = False
        self.move_is_long_castle = False
        self.is_promoting = False
        self.black_jail_x, self.black_jail_y = JAIL_START_X, BLACK_JAIL_Y
        self.white_jail_x, self.white_jail_y = JAIL_START_X, WHITE_JAIL_Y
        for row in range(8):
            for col in range(8):
                piece = self.chess_board.get(row, col)
                if piece == chess.EMPTY:
                    continue
                x, y = board_to_screen(row, col)
                tile = get_piece_tile(piece)
                new = Sprite(tile, x, y, 2)
                new.row = row
                new.col = col
                new.piece = piece
                self.pieces.append(new)

    def note_event (self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                self.do_short_castle = True
            elif event.key == pygame.K_k:
                self.do_long_castle = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x = event.pos[0] // 2
            y = event.pos[1] // 2
            if self.is_promoting:
                self.selected_piece = None
                for piece in self.pieces:
                    rect = pygame.Rect(piece.x, piece.y, piece.size * 8, piece.size * 8)
                    if rect.collidepoint((x, y)):
                        self.selected_piece = piece
            else:
                rowcol = screen_to_board(x, y)
                if rowcol:
                    selected_piece = self.chess_board.get(*rowcol)
                    selected_team = chess.piece_team(selected_piece)
                    current_team = self.chess_board.get_current_team()
                    selected_is_team = current_team == selected_team
                    if self.selected_start is None:
                        if selected_is_team:
                            # Make a start selection
                            self.selected_start = rowcol
                        else:
                            self.play_sound('error')
                    else:
                        if selected_is_team:
                            # Override start selection
                            self.selected_start = rowcol
                            self.selected_end = None
                        else:
                            # Make an end selection
                            self.selected_end = rowcol

    def move_piece_grid (self, piece, row, col):
        piece.row = row
        piece.col = col
        x, y = board_to_screen(row, col)
        self.move_piece(piece, x, y)

    def move_piece (self, piece, x, y):
        piece.x = x
        piece.y = y

    def remove_piece (self, piece):
        piece.row = None
        piece.col = None
        if chess.piece_team(piece.piece) == chess.WHITE_KING:
            piece.x = self.white_jail_x
            piece.y = self.white_jail_y
            self.white_jail_x += 16
            if self.white_jail_x >= JAIL_END_X:
                self.white_jail_x = JAIL_START_X
                self.white_jail_y += 16
        else:
            piece.x = self.black_jail_x
            piece.y = self.black_jail_y
            self.black_jail_x += 16
            if self.black_jail_x >= JAIL_END_X:
                self.black_jail_x = JAIL_START_X
                self.black_jail_y -= 16

    def update (self):
        self.clock.tick(30) # 30 FPS
        team = self.chess_board.get_current_team()
        if self.game_over:
            return
        elif self.chess_board.get_winner():
            self.game_over = True
        elif self.is_promoting:
            if self.selected_piece is not None:
                piece = self.selected_piece.piece
                new_role = chess.piece_role(piece)
                piece = chess.role_as_team(new_role, team)
                if self.chess_board.can_promote(team, *self.move_end, new_role):
                    self.chess_board.promote(team, *self.move_end, new_role)
                    promote_piece = self.get_piece_at(*self.move_end)
                    promote_piece.piece = piece
                    promote_piece.tile = get_piece_tile(piece)
                    self.is_promoting = False
                    # Finish the rest of the post-move logic
                    self.move_start = None
                    self.move_end = None
                    self.chess_board.turn += 1
                    self.play_sound('promote')
                self.selected_piece = None
        elif self.move_start is not None and self.move_end is not None:
            if self.move_is_long_castle or self.move_is_short_castle:
                king = self.get_piece_at(*self.move_start)
                self.move_piece_grid(king, *self.move_end)
                if self.move_is_long_castle:
                    castle = self.get_piece_at(self.move_start[0], 0)
                    self.move_piece_grid(castle, self.move_end[0], self.move_end[1] + 1)
                    self.chess_board.move_castle_long(team)
                else:
                    castle = self.get_piece_at(self.move_start[0], 7)
                    self.move_piece_grid(castle, self.move_end[0], self.move_end[1] - 1)
                    self.chess_board.move_castle_short(team)
                self.chess_board.turn += 1
                self.play_sound('castle')
                self.move_start = None
                self.move_end = None
                self.move_is_long_castle = self.move_is_short_castle = False
            else:
                piece = self.get_piece_at(*self.move_start)
                target = self.get_piece_at(*self.move_end)
                self.move_piece_grid(piece, *self.move_end)
                is_capture = False
                if target is not None:
                    self.remove_piece(target)
                    is_capture = True
                self.chess_board.move(*self.move_start, *self.move_end)
                if self.chess_board.is_promotable(team, *self.move_end):
                    self.is_promoting = True
                    self.play_sound('can promote')
                else:
                    self.move_start = None
                    self.move_end = None
                    self.chess_board.turn += 1
                    self.play_resulting_sound(is_capture)
        elif self.selected_start is not None and self.selected_end is not None:
            piece = self.chess_board.get(*self.selected_start)
            if self.chess_board.is_legal_move(team, *self.selected_start, *self.selected_end):
                self.move_start = self.selected_start
                self.move_end = self.selected_end
                self.selected_start = None
                self.selected_end = None
            elif self.chess_board.king_can_castle_long(team):
                king_row, king_col = self.chess_board.find_piece(team)
                if self.selected_start == (king_row, king_col):
                    if self.selected_end == (king_row, king_col - 2):
                        self.move_is_long_castle = True
                        self.move_start = self.selected_start
                        self.move_end = self.selected_end
                        self.selected_start = None
                        self.selected_end = None
            elif self.chess_board.king_can_castle_short(team):
                king_row, king_col = self.chess_board.find_piece(team)
                if self.selected_start == (king_row, king_col):
                    if self.selected_end == (king_row, king_col + 2):
                        self.move_is_short_castle = True
                        self.move_start = self.selected_start
                        self.move_end = self.selected_end
                        self.selected_start = None
                        self.selected_end = None
            else:
                self.selected_start = None
                self.selected_end = None
                self.play_sound('error')
        self.update_message()

    def play_resulting_sound (self, is_capture):
        sound = None
        if self.chess_board.king_is_in_check(self.chess_board.get_current_team()):
            if self.chess_board.get_winner():
                sound = 'checkmate'
            else:
                sound = 'check'
        else:
            if is_capture:
                sound = 'capture'
            else:
                sound = 'move'
        self.play_sound(sound)

    def display (self):
        for i, tile in enumerate(BACKGROUND):
            x = 8 * (i % 32)
            y = 8 * (i // 32)
            draw_tile(self.screen, self.spritesheet, tile, x, y)
        for piece in self.pieces:
            draw_tile(self.screen, self.spritesheet, piece.tile, piece.x, piece.y, piece.size)
        for s in self.message_sprites:
            draw_tile(self.screen, self.spritesheet, s.tile, s.x, s.y)

    def get_piece_at (self, row, col):
        for piece in self.pieces:
            if piece.row == row and piece.col == col:
                return piece

    def next_turn (self):
        self.moving_piece = None
        self.moving_start = None
        self.moving_end = None
        self.selected_end = None
        self.selected_start = None
        self.turn += 1
        
def get_sprite (spritesheet, sprite_id, sprite_size):
    x = 8 * (sprite_id % 32)
    y = 8 * (sprite_id // 32)
    size = sprite_size * 8
    return spritesheet.subsurface((x, y, size, size))

def get_piece_tile (piece):
    i = 20
    if chess.piece_team(piece) == chess.BLACK_KING:
        i += 128
    role = chess.piece_role(piece)
    if role == chess.WHITE_BISHOP:
        i += 2
    elif role == chess.WHITE_KNIGHT:
        i += 4
    elif role == chess.WHITE_ROOK:
        i += 6
    elif role == chess.WHITE_QUEEN:
        i += 8
    elif role == chess.WHITE_KING:
        i += 10
    return i

def screen_to_board (x, y):
    col = (x - CORNER_X) // GRID_SIZE
    row = (y - CORNER_Y) // GRID_SIZE
    if (col in range(8)) and (row in range(8)):
        return (row, col)

def board_to_screen (row, col):
    if (col in range(8)) and (row in range(8)):
        x = CORNER_X + col * GRID_SIZE
        y = CORNER_Y + row * GRID_SIZE
        return (x, y)

def draw_tile (screen, spritesheet, tile, x, y, size=1):
    img = get_sprite(spritesheet, tile, size)
    screen.blit(img, (x, y))

def is_on_board (row, col):
    return row in range(8) and col in range(8)

def display_init ():
    pygame.display.init()
    icon = pygame.image.load('icon.png')
    width, height = 256*2, 240*2 # NES resolution
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Chess')
    return pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)

def game_quit ():
    pygame.quit()

def char_to_tile (char):
    order = '$#abcdefghijklmnopqrstuvwxyz0123______456789-:!,.%@? '
    return 256 + order.index(char)

def main ():
    pygame.init()
    screen = display_init()
    screen2 = pygame.Surface((256*2, 240*2))
    game = Game(screen)
    while game.running:
        for event in pygame.event.get():
            game.note_event(event)
        game.update()
        game.display()
        small = screen.subsurface((0, 0, 256, 240))
        pygame.transform.scale(small, (256*2, 240*2), screen2)
        screen.blit(screen2, (0, 0))
        pygame.display.update()
    game_quit()

if __name__ == '__main__':
    main()
