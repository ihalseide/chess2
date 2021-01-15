#!/usr/bin/env python3

import os
import pygame
import chess

from pygame import Rect

class Sprite (pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.rect = pygame.Rect(x, y, width, height)
        iw, ih = image.get_rect().size
        self.image = image

def image_load (name):
    return pygame.image.load(os.path.join('sprites', name))

def sound_load (name):
    return pygame.mixer.Sound(os.path.join('sounds', name))

def display_init ():
    width, height = 640, 480
    pygame.init()
    pygame.display.init()
    icon = pygame.image.load('icon.png')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Chezz.exe')
    return pygame.display.set_mode((width, height))

class State:
    debug_init = False

    def __init__ (self, next_state=None):
        if self.debug_init:
            print('starting state', self)
        self.is_done = False
        self.next_state = next_state
        self.is_quit = False

    def note_event (self, event):
        pass

    def display (self, screen):
        pass

    def update (self):
        pass

class OptionState (State):
    @classmethod
    def load (cls):
        pygame.mixer.music.load(os.path.join('sounds', 'lobby_music.ogg'))

    def __init__ (self):
        State.__init__(self, next_state=PlayState)
        # pygame.mixer.music.play(-1)
        self.is_done = True

class PlayState (State):
    debug_corner = False
    debug_select = False

    corner_x, corner_y = 128, 32 
    square_size = 48
    board_image_size = 416

    @classmethod
    def load (cls):
        cls.board_image = image_load('board.png')
        cls.white_sprites = image_load('american_team.png')
        cls.black_sprites = image_load('black_team.png')
        cls.selection_img = image_load('select_square.png')

    def __init__ (self):
        State.__init__(self, next_state=MenuState)
        self.chess_board = chess.Board()
        self.move_log = []
        self.turn = 0
        self.selected_start = None
        self.selected_end = None
        self.background_sprites = pygame.sprite.Group()
        self.piece_sprites = pygame.sprite.Group()
        self.floating_sprites = pygame.sprite.Group()
        self.spawn_pieces()
        self.board_sprite = Sprite(self.corner_x - 16, self.corner_y - 16, self.board_image_size, self.board_image_size,
                self.board_image, [self.background_sprites])
        self.board_rect = self.board_sprite.rect.inflate(-32, -32)
        self.selection_sprite = Sprite(0, 0, 32, 32, self.selection_img, self.floating_sprites)
        self.do_short_castle = False
        self.do_long_castle = False

    def get_current_team (self):
        if self.turn % 2 == 0:
            return chess.WHITE_KING
        else:
            return chess.BLACK_KING

    def spawn_pieces (self):
        offset = 8
        size = 32
        group = self.piece_sprites

        # For when there are already sprites
        self.piece_sprites.empty()

        for row in range(self.chess_board.rows):
            for col in range(self.chess_board.columns):
                piece = self.chess_board.get(row, col)
                if piece == chess.EMPTY:
                    continue
                if chess.piece_team(piece) == chess.WHITE_KING:
                    sheet = self.white_sprites
                else:
                    sheet = self.black_sprites
                sheet_x = size * (chess.piece_role(piece) - 1)
                img = sheet.subsurface((sheet_x, 0, size, size))
                x, y = self.board_to_screen(row, col)
                sprite = Sprite(x + offset, y + offset, size, size, img, group)
                sprite.row = row
                sprite.col = col
                sprite.piece = piece

    def screen_to_board (self, x, y):
        if self.board_rect.collidepoint((x, y)):
            row = (y - self.corner_y) // self.square_size
            col = (x - self.corner_x) // self.square_size
            return row, col

    def board_to_screen (self, row, col):
        if self.chess_board.in_range(row, col):
            x = col * self.square_size + self.corner_x
            y = row * self.square_size + self.corner_y
            return x, y

    def note_event (self, event):
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
                if self.debug_select:
                    name = lambda s: chess.name_square(*s) if s else s
                    print(name(self.selected_start), '-->', name(self.selected_end))

    def update (self):
        board_update = False
        if None not in (self.selected_start, self.selected_end):
            if self.debug_select:
                print('try a move...', end=' ')
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

    def next_turn (self):
        self.turn += 1
        self.spawn_pieces()
        self.selected_start = None
        self.selected_end = None

    def display (self, screen):
        screen.fill((120, 120, 120))

        self.background_sprites.draw(screen)
        self.piece_sprites.draw(screen)
        self.floating_sprites.draw(screen)

        if self.debug_corner:
            pygame.draw.rect(screen, (0, 255, 255), (self.corner_x, self.corner_y, 10, 10))

        pygame.display.update()

class MenuState (State):
    @classmethod
    def load (cls):
        cls.press_img = image_load('press.png').convert_alpha()
        cls.title_img = image_load('title.png').convert_alpha()
        cls.notice_img = image_load('notice.png').convert_alpha()

    def __init__ (self):
        State.__init__(self, next_state=OptionState)
        width = 640
        self.bar1 = Rect(0, 0, width, 60)
        self.bar2 = Rect(0, self.bar1.bottom, width, 320)
        self.bar3 = Rect(0, self.bar2.bottom, width, 22)
        self.bar4 = Rect(0, self.bar3.bottom, width, 80)
        self._init_sprites(self.bar3.y + 1, self.bar2.y + 30, self.bar4.y)
        self.show_press = True
        self.is_button_pressed = False
        self.is_end = False

        self.done_event = pygame.USEREVENT + 2
        self.done_delay = 900
        # Timer to trigger the press sprite showing
        self.press_event = pygame.USEREVENT + 1
        self.press_delay = 800
        pygame.time.set_timer(self.press_event, self.press_delay)

    def note_event (self, event):
        if event.type == self.press_event:
            self.show_press = not self.show_press
        elif event.type == self.done_event:
            self.is_done = True
        elif event.type == pygame.KEYDOWN:
            self.is_button_pressed = True

    def _init_sprites (self, y1, y2, y3):
        self.main_sprites = pygame.sprite.Group()
        self.press_sprite = pygame.sprite.Group()

        press = Sprite(0, y1, 192, 20, self.press_img, [self.press_sprite])
        press.rect.centerx = 320
        
        title = Sprite(0, y2, 640, 150, self.title_img, [self.main_sprites])
        title.rect.centerx = 320

        notice = Sprite(0, y3, 640, 100, self.notice_img, [self.main_sprites])

    def update (self):
        if self.is_button_pressed:
            if not self.is_end:
                self.is_end = True
                self.show_press = False
                pygame.time.set_timer(self.press_event, 0)
                pygame.time.set_timer(self.done_event, self.done_delay, True)
                sound_load('slip.wav').play()

    def display (self, screen):
        black = 0, 0, 0
        white = 255, 255, 255
        red = 240, 10, 10
        pygame.draw.rect(screen, black, self.bar1)
        pygame.draw.rect(screen, white, self.bar2)
        pygame.draw.rect(screen, red, self.bar3)
        pygame.draw.rect(screen, black, self.bar4)
        self.main_sprites.draw(screen)
        if self.show_press:
            self.press_sprite.draw(screen)
        pygame.display.update()

def main ():
    screen = display_init()
    MenuState.load()
    PlayState.load()
    state = MenuState()
    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            state.note_event(event)
            if event.type == pygame.QUIT:
                running = False
        state.update()
        state.display(screen)
        if state.is_quit:
            running = False
        elif state.is_done:
            new_state = state.next_state()
            state = new_state
    pygame.quit()

if __name__ == '__main__':
    main()
