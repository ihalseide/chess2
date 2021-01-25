#!/usr/bin/env python3

import pygame
import chess

CORNER_X, CORNER_Y = 24, 24 
SQUARE_SIZE = 16
WIN_TEXT = [
        "You can now play as Luigi",
        "Free Play unlocked"
        ]

LOSE_TEXT = [
        "All your base are belong to us",
        "Sorry, mate",
        "Screams echo around you"
        ]
BACKGROUND = [
326,326,326,326,326,326,306,286,284,286,285,326,266,283,258,268,326,265,258,269,276,262,266,261,262,326,326,326,326,326,326,326
326,326,326,326,326,326,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,326,326,326,326,326,326
326,326,326,326,326,326,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,326,326,326,326,326,326
326,326,326,326,326,326,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,326,326,326,326,326,326
326,326,326,326,326,326,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,326,326,326,326,326,326
326,326,326,326,326,326,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,326,326,326,326,326,326
326,326,326,326,326,326,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,326,326,326,326,326,326
326,326,326,326,326,326,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,326,326,326,326,326,326
326,326,326,326,326,326,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,326,326,326,326,326,326
326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326
326,326,326,326,326,326,326,288,289,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,293,326,326,326,326,326,326,326
326,326,326,326,326,326,326,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,325,326,326,326,326,326,326,326
326,326,326,326,326,326,298,320,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,357,326,326,326,326,326,326,326
326,326,326,326,326,326,326,320,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,389,326,326,326,326,326,326,326
326,326,326,326,326,326,297,320,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,326,326,326,326,326,326,326
326,326,326,326,326,326,326,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,421,326,326,326,326,326,326,326
326,326,326,326,326,326,296,320,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,421,326,326,326,326,326,326,326
326,326,326,326,326,326,326,320,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,421,326,326,326,326,326,326,326
326,326,326,326,326,326,295,320,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,326,326,326,326,326,326,326
326,326,326,326,326,326,326,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,421,326,326,326,326,326,326,326
326,326,326,326,326,326,294,320,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,421,326,326,326,326,326,326,326
326,326,326,326,326,326,326,320,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,421,326,326,326,326,326,326,326
326,326,326,326,326,326,287,320,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,326,326,326,326,326,326,326
326,326,326,326,326,326,326,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,421,326,326,326,326,326,326,326
326,326,326,326,326,326,286,352,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,421,326,326,326,326,326,326,326
326,326,326,326,326,326,326,384,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,421,326,326,326,326,326,326,326
326,326,326,326,326,326,285,416,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,326,326,326,326,326,326,326
326,326,326,326,326,326,326,448,449,449,449,449,449,449,449,449,449,449,449,449,449,450,451,452,453,326,326,326,326,326,326,326
326,326,326,326,326,326,326,326,258,326,259,326,260,326,261,326,262,326,263,326,264,326,265,326,326,326,326,326,326,326,326,326
326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326,326
]


class Sprite:

    def __init__(self, sprite_id, x, y, sprite_size, z=0):
        global game
        self.x = x
        self.y = y
        self.z = z
        self.sprite_id = sprite_id
        self.sprite_size = sprite_size
        self.image = get_sprite(self.sprite_id, self.sprite_size)
    
    def draw (self, screen):
        screen.blit(self.image, (self.x, self.y))

def get_sprite (sprite_id, sprite_size):
    global game
    x = sprite_id % 32
    y = sprite_id // 32
    size = sprite_size * 8
    return game.spritesheet.subsurface((x, y, size, size))

def game_init ():
    global game
    game.screen = display_init()
    game.state = PlayState()
    game.clock = pygame.time.Clock()
    game.running = True
    game.spritesheet = pygame.image.load('spritesheet.png')
    game.sprites = []
    game.chess_board = chess.Board()
    game.move_log = []
    game.turn = 0
    game.selected_start = None
    game.selected_end = None
    game.do_short_castle = False
    game.do_long_castle = False
    game_init_background()
    game_init_pieces()

def game_init_background ():
    global game
    game.background = []
    width, height = 32, 30
    for x in range(width):
        for y in range(height):
            i = x + y * width
            game.background.append(Sprite(i, x * 8, y * 8, 1))

def game_init_pieces ():
    for row in range(8):
        for col in range(8):
            piece = game.chess_board.get(row, col)
            if piece == chess.EMPTY:
                continue
            x, y = game.board_to_screen(row, col)
            pass

def get_current_team ():
    global game
    if game.turn % 2 == 0:
        return chess.WHITE_KING
    else:
        return chess.BLACK_KING

def screen_to_board (x, y):
    pass

def board_to_screen (row, col):
    pass

def note_event (event):
    global game
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_c:
            self.do_short_castle = True
        elif event.key == pygame.K_k:
            self.do_long_castle = True
    elif event.type == pygame.MOUSEBUTTONDOWN:
        rowcol = self.screen_to_board(*event.pos)
        if rowcol:
            selected_piece = self.chess_board.get(*rowcol)
            selected_team = chess.piece_team(selected_piece)
            selected_is_on_team = self.get_current_team() == selected_team
            if self.selected_start is None:
                if selected_is_on_team:
                    # Make a start selection
                    self.selected_start = rowcol
            else:
                if selected_is_on_team:
                    # Override start selection
                    self.selected_start = rowcol
                    self.selected_end = None
                else:
                    # Make an end selection
                    self.selected_end = rowcol

def update ():
    global game
    board_update = False
    if None not in (self.selected_start, self.selected_end):
        if self.chess_board.is_legal_move(self.get_current_team(), *self.selected_start, *self.selected_end):
            self.chess_board.move(*self.selected_start, *self.selected_end)
            log_from = chess.name_square(*self.selected_start)
            log_to = chess.name_square(*self.selected_end)
            self.move_log.append('{} to {}'.format(log_from, log_to))
            board_update = True
        self.selected_start = None
        self.selected_end = None
    else:
        if self.do_short_castle:
            self.do_short_castle = False
            team = self.get_current_team()
            if self.chess_board.king_can_castle_short(team):
                self.chess_board.move_castle_short(team)
                board_update = True
                self.move_log.append('O-O')
        elif self.do_long_castle:
            self.do_long_castle = False
            team = self.get_current_team()
            if self.chess_board.king_can_castle_long(team):
                self.chess_board.move_castle_long(team)
                board_update = True
                self.move_log.append('O-O-O')
    if board_update:
        self.next_turn()

def next_turn ():
    global game
    game.turn += 1
    game.selected_start = None
    game.selected_end = None

def display (screen):
    global game
    print('display')
    pygame.display.update()

def is_on_board (row, col):
    return row in range(8) and col in range(8)

def display_init ():
    pygame.display.init()
    icon = pygame.image.load('icon.png')
    width, height = 256, 240 # NES resolution
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Chess')
    return pygame.display.set_mode((width, height))

def game_loop ():
    global game
    game.clock.tick(30)
    for event in pygame.event.get():
        note_event(event)
        if event.type == pygame.QUIT:
            game.running = False
    update()
    display(screen)

def game_quit ():
    pygame.quit()

def main ():
    global game
    game = object()
    pygame.init()
    game_init()
    while game.running:
        game_loop()
    game_quit()

if __name__ == '__main__':
    main()
