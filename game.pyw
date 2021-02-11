#!/usr/bin/env python3 

import pygame, os, threading, random, sys
import chess, chess_ai
from backgrounds import *

WIDTH, HEIGHT = 256, 240
SCALE = 2
FPS = 30 # Frames Per Seconds
CORNER_X, CORNER_Y = 64, 56
GRID_SIZE = 16
MESSAGE_X, MESSAGE_Y = 40, 32 
JAIL_START_X, JAIL_END_X = 200, 248
BLACK_JAIL_Y = 200
WHITE_JAIL_Y = 40
GAME_OVER_TEXT = [
        "you can now play as luigi",
        "free play unlocked",
        "all your base are belong to us",
        "i'm king of the world!",
        "i'll be back"
        ]

class Sprite:

    def __init__(self, tile, x, y, size=1):
        self.tile = tile
        self.x = x
        self.y = y
        self.size = size

class Game:

    def __init__ (self, screen, spritesheet):
        self.debug = False
        self.screen = screen
        self.spritesheet = spritesheet
        self.running = True
        self.state = 'menu'
        self.valid_states = ('menu', 'transition', 'play', 'wait', 'move', 'promote', 'queenside castle',
                'kingside castle', 'mate', 'resign', 'choose team', 'game over')
        self.init_sounds()
        self.enter_state(self.state)

    def is_play_state (self, state):
        return state in ('play', 'wait', 'move', 'promote', 'queenside castle',
                'kingside castle', 'mate', 'castle the rook', 'resign', 'choose team')

    def init_chess (self): 
        self.chess_board = chess.Game()
        self.black_is_ai = False
        self.white_is_ai = False

    def init_message (self):
        self.message = None
        self.message_sprites = []
        self.update_message()
    
    def get_message (self):
        assert self.state in self.valid_states
        is_white = self.chess_board.get_current_team() == chess.WHITE_KING
        state = self.state
        if state == 'game over':
            return random.choice(GAME_OVER_TEXT)
        if state == 'choose team':
            return 'select the pieces to lead' 
        elif state == 'promote':
            if is_white:
                return 'white# pawn promotion'
            else:
                return 'black$ pawn promotion'
        elif state == 'mate' or state == 'resign':
            winner = self.chess_winner
            if winner == chess.WHITE_KING:
                return 'white# checkmates black$!'
            elif winner == chess.BLACK_KING:
                return 'black$ checkmates white#!'
            else:
                if self.chess_board.is_king_in_stalemate(chess.WHITE_KING):
                    return 'white# is in stalemate'
                elif self.chess_board.is_king_in_stalemate(chess.BLACK_KING):
                    return 'black$ is in stalemate'
                else:
                    return 'game ended'
        elif state == 'wait':
            if is_white:
                if self.chess_board.is_king_in_check(chess.WHITE_KING):
                    return 'white# is in check'
                elif self.chess_board.move_num == 0:
                    return 'white# to make 1st move'
                else:
                    return 'white# to move'
            else:
                if self.chess_board.is_king_in_check(chess.BLACK_KING):
                    return 'black$ is in check'
                else:
                    return 'black$ to move'

    def update_message (self):
        message = self.get_message() 
        if message != self.message:
            self.message = message
            self.create_message_sprites()

    def create_message_sprites (self):
        self.message_sprites = []
        for i, char in enumerate(self.message):
            tile = char_to_tile(char)
            s = Sprite(tile, MESSAGE_X + i * 8, MESSAGE_Y, 1)
            self.message_sprites.append(s)

    def init_sounds (self):
        names = ['check', 'checkmate', 'error', 'move', 'promote', 'can promote',
                'capture', 'castle', 'resign', 'reveal', 'game over']
        sound = lambda name: pygame.mixer.Sound(os.path.join('sound', name))
        self.sounds = {name: sound(name + '.wav') for name in names}

    def play_sound (self, name):
        self.sounds[name].play()

    def init_timers (self):
        self.white_ticks = 0
        self.white_seconds = 0
        self.white_minutes = 0
        self.black_ticks = 0
        self.black_seconds = 0
        self.black_minutes = 0

    def init_capturing_area (self):
        self.black_jail_x, self.black_jail_y = JAIL_START_X, BLACK_JAIL_Y
        self.white_jail_x, self.white_jail_y = JAIL_START_X, WHITE_JAIL_Y

    def init_movement (self): 
        # Input
        self.input_x = None
        self.input_y = None
        self.input_is_fresh = False
        # Used for the selected piece and destination
        self.selected_sprite = None
        self.selected_start = None
        self.selected_end = None
        # Used for moving the selected piece
        self.moving_steps = None
        self.moving_dx = None
        self.moving_dy = None

    def enter_state (self, state):
        assert state in self.valid_states
        self.state = state
        if state == 'menu':
            self.set_background(MENU_BACKGROUND)
            self.num_players = None
            self.show_option_0 = False
            self.trigger_option_0_rect = pygame.Rect(72, 224, 8, 8)
            self.option_0_rect = pygame.Rect(96, 120, 64, 8)
            self.option_1_rect = pygame.Rect(96, 136, 64, 8)
            self.option_2_rect = pygame.Rect(96, 152, 64, 8)
            self.cursor_y = 256 
        elif state == 'transition': 
            self.move_steps = 100
            self.state = 'transition'
            self.set_background(TRANSITION_BACKGROUND)
            self.init_movement()
            self.init_chess()
            self.init_timers()
            self.init_capturing_area()
            self.init_pieces()
            self.highlight_sprites = []
            self.init_message()
        elif state == 'play':
            self.set_background(GAME_BACKGROUND)
            if self.num_players == 1:
                self.enter_state('choose team')
            else:
                if self.num_players == 0:
                    self.black_is_ai = self.white_is_ai = True
                self.enter_state('wait')
        elif state == 'choose team':
            self.selected_sprite = None
            self.selected_start = None
            self.selected_end = None
            self.moving_steps = None
            self.moving_dx = None
            self.moving_dy = None
            self.input_is_fresh = False
            self.input_x = self.input_y = None
            self.highlight_sprites = [] 
            self.update_message() 
        elif state == 'wait':
            # Check for Check here
            self.selected_sprite = None
            self.selected_start = None
            self.selected_end = None
            self.moving_steps = None
            self.moving_dx = None
            self.moving_dy = None
            self.input_is_fresh = False
            self.input_x = self.input_y = None
            self.highlight_sprites = []
            # Check for Checkmate
            if self.chess_board.is_king_in_check(self.chess_board.get_current_team()):
                self.play_sound('check')
            if self.chess_board.is_game_over():
                self.chess_winner = self.chess_board.get_winner()
                self.enter_state('mate')
                return
            self.update_message()
        elif state == 'move':
            assert self.selected_sprite and self.selected_start and self.selected_end
            start_x, start_y = board_to_screen(*self.selected_start)
            end_x, end_y = board_to_screen(*self.selected_end)
            self.moving_steps = 8
            self.moving_dx = (end_x - start_x) // self.moving_steps
            self.moving_dy = (end_y - start_y) // self.moving_steps 
        elif state == 'promote':
            assert self.selected_sprite and self.selected_start and self.selected_end 
            self.update_message() 
        elif state in ('queenside castle', 'kingside castle'):
            assert self.selected_sprite and self.selected_start and self.selected_end 
            team = chess.get_current_team(self.chess_board.move_num)
            king_square = self.chess_board.find_piece(team)
            can_castle = (
                    (state == 'kingside castle' and self.chess_board.can_castle_kingside(*king_square))
                    or
                    (state == 'queenside castle' and self.chess_board.can_castle_queenside(*king_square)))
            if can_castle:
                start_x, start_y = board_to_screen(*self.selected_start)
                end_x, end_y = board_to_screen(*self.selected_end)
                self.moving_steps = 4
                self.moving_dx = (end_x - start_x) // self.moving_steps
                self.moving_dy = (end_y - start_y) // self.moving_steps
                self.castle_state = 'king'
            else:
                self.play_sound('error')
                self.enter_state('wait') 
        elif state == 'mate':
            self.sound_delay = 16 
            self.update_message()
        elif state == 'resign':
            self.play_sound('resign') 
            self.move_steps = 32
            self.overlay_surf = pygame.Surface((WIDTH, HEIGHT))
            self.overlay_surf.set_colorkey((255, 255, 255))
            losing_king = self.chess_board.get_current_team()
            losing_coords = self.chess_board.find_piece(losing_king)
            king_sprite = self.get_sprite_at(*losing_coords)
            self.target_x, self.target_y = king_sprite.x + 8, king_sprite.y + 8
        elif state == 'game over': 
            self.move_steps = 180
            self.set_background(GAME_OVER_BACKGROUND)
        else:
            # If this point is reached, I made a typo in the above if-statements
            raise SyntaxError() 

    def init_pieces (self):
        self.pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.chess_board.get(row, col)
                if piece != chess.EMPTY:
                    tile = get_piece_tile(piece)
                    x, y = board_to_screen(row, col)
                    new = Sprite(tile, x, y, size=2)
                    new.row = row
                    new.col = col
                    new.piece = piece
                    self.pieces.append(new)

    def note_event (self, event):
        if self.debug and event.type == pygame.KEYDOWN:
            k = event.key
            if k == pygame.K_d:
                print('state:', self.state, ', player #:', self.num_players)
        if self.state == 'menu':
            if event.type == pygame.MOUSEBUTTONDOWN:
                xy = event.pos[0] // SCALE, event.pos[1] // SCALE
                if self.trigger_option_0_rect.collidepoint(xy):
                    if not self.show_option_0:
                        self.set_background(MENU_BACKGROUND_2)
                        self.play_sound('reveal')
                    self.show_option_0 = True
                elif self.show_option_0 and self.option_0_rect.collidepoint(xy):
                    self.num_players = 0
                elif self.option_1_rect.collidepoint(xy):
                    self.num_players = 1
                elif self.option_2_rect.collidepoint(xy):
                    self.num_players = 2
                elif xy[0] == xy[1] == 0:
                    self.play_sound('reveal')
                    self.debug = True
                if self.num_players is not None:
                    self.enter_state('transition')
            elif event.type == pygame.MOUSEMOTION:
                xy = event.pos[0] // SCALE, event.pos[1] // SCALE
                if self.show_option_0 and self.option_0_rect.collidepoint(xy):
                    self.cursor_y = 120
                elif self.option_1_rect.collidepoint(xy):
                    self.cursor_y = 136
                elif self.option_2_rect.collidepoint(xy):
                    self.cursor_y = 152 
        elif self.state == 'transition':
            pass
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.input_x, self.input_y = event.pos[0] // SCALE, event.pos[1] // SCALE
                self.input_is_fresh = True

    def move_sprite_on_board (self, sprite, row, col):
        assert row in range(8) and col in range(8)
        sprite.row, sprite.col = row, col
        x, y = board_to_screen(row, col)
        sprite.x, sprite.y = x, y

    def remove_sprite (self, sprite):
        sprite.row = None
        sprite.col = None
        if chess.get_piece_team(sprite.piece) == chess.WHITE_KING:
            sprite.x = self.white_jail_x
            sprite.y = self.white_jail_y
            self.white_jail_x += 16
            if self.white_jail_x >= JAIL_END_X:
                self.white_jail_x = JAIL_START_X
                self.white_jail_y += 16
        else:
            sprite.x = self.black_jail_x
            sprite.y = self.black_jail_y
            self.black_jail_x += 16
            if self.black_jail_x >= JAIL_END_X:
                self.black_jail_x = JAIL_START_X
                self.black_jail_y -= 16

    def update_timers (self): 
        if self.chess_board.move_num == 0:
            # Don't time before the first move is made by white
            return
        elif chess.get_current_team(self.chess_board.move_num) == chess.BLACK_KING:
            self.black_ticks += 1
            if self.black_ticks >= FPS:
                self.black_ticks = 0
                self.black_seconds += 1
                if self.black_seconds >= 60:
                    self.black_seconds = 0
                    self.black_minutes += 1
        else:
            self.white_ticks += 1
            if self.white_ticks >= FPS:
                self.white_ticks = 0
                self.white_seconds += 1
                if self.white_seconds >= 60:
                    self.white_seconds = 0
                    self.white_minutes += 1

    def update_game_choose (self):
        assert self.num_players == 1
        if self.input_is_fresh:
            self.input_is_fresh = False
            rowcol = screen_to_board(self.input_x, self.input_y)
            if rowcol:
                piece = self.chess_board.get(*rowcol)
                if chess.is_piece(piece):
                    team = chess.get_piece_team(piece)
                    if team == chess.BLACK_KING:
                        self.white_is_ai = True
                        self.black_is_ai = False
                    else:
                        self.white_is_ai = False
                        self.black_is_ai = True
                    self.enter_state('wait') 

    def update_game_wait (self): 
        # Validate selection of pieces and moves
        self.update_timers() 
        if self.is_ai_turn():
            team = self.chess_board.get_current_team()
            row, col, to_row, to_col = chess_ai.get_move(self.chess_board, team)
            self.selected_start = row, col
            self.selected_end = to_row, to_col 
            self.selected_sprite = self.get_sprite_at(*self.selected_start)
        elif self.input_is_fresh:
            self.input_is_fresh = False
            rowcol = screen_to_board(self.input_x, self.input_y)
            if rowcol:
                current_team = self.chess_board.get_current_team()
                sprite = self.get_sprite_at(*rowcol)
                is_team_mate = (sprite is not None) and (current_team == chess.get_piece_team(sprite.piece))
                if is_team_mate:
                        self.selected_start = rowcol
                        self.create_highlight_sprites()
                else:
                    if self.selected_start:
                        self.selected_end = rowcol
                    else:
                        self.play_sound('error')
                        self.enter_state('wait')
            else:
                # Clicking off of the board --> deselect everything
                self.enter_state('wait')
        if self.selected_start:
            if self.selected_end:
                # Validate start of selection
                self.selected_sprite = self.get_sprite_at(*self.selected_start) # could be None
                target_sprite = self.get_sprite_at(*self.selected_end) # could be None
                current_team = self.chess_board.get_current_team()
                is_legal_move = self.chess_board.is_legal_move(current_team, *self.selected_start, *self.selected_end)
                if is_legal_move:
                    castle = self.chess_board.move_is_castling(*self.selected_start, *self.selected_end)
                    if castle == chess.WHITE_QUEEN: 
                        self.enter_state('queenside castle')
                    elif castle == chess.WHITE_KING:
                        self.enter_state('kingside castle')
                    else:
                        self.enter_state('move')
                else:
                    self.play_sound('error')
                    self.enter_state('wait')

    def update_game_move (self):
        assert self.selected_sprite and self.selected_start and self.selected_end
        assert None not in (self.moving_dx, self.moving_dy, self.moving_steps)
        if self.moving_steps > 0:
            # Move the sprite a little
            self.moving_steps -= 1
            self.selected_sprite.x += self.moving_dx
            self.selected_sprite.y += self.moving_dy
        else:
            # Remove the captured sprite (if any)
            target = None
            if self.chess_board.move_is_en_passant(*self.selected_start, *self.selected_end):
                target_square = chess.get_en_passant_capture(*self.selected_start, *self.selected_end)
                target = self.get_sprite_at(*target_square)
            else:
                target = self.get_sprite_at(*self.selected_end) 
            if target:
                self.remove_sprite(target)
            # Finalize the moving sprite
            self.move_sprite_on_board(self.selected_sprite, *self.selected_end)
            # Update the chess board
            self.chess_board.make_move(*self.selected_start, *self.selected_end)
            if self.chess_board.is_promotable(*self.selected_end):
                self.play_sound('can promote')
                self.enter_state('promote')
            else:
                if self.chess_board.is_king_in_check(self.chess_board.get_current_team()):
                    self.play_sound('check')
                elif target: 
                    self.play_sound('capture')
                else:
                    self.play_sound('move')
                self.enter_state('wait')

    def update_game_promote (self): 
        if self.is_ai_turn():
            self.play_sound('promote')
            # AI always chooses the queen here
            self.chess_board.set(*self.selected_end, chess.role_as_team(chess.WHITE_QUEEN, team))
            #self.turn += 1
            self.enter_state('wait') 
        elif self.input_is_fresh:
            self.input_is_fresh = False
            self.selected_sprite = None
            for sprite in self.pieces:
                rect = pygame.Rect(sprite.x, sprite.y, 16, 16)
                if rect.collidepoint(self.input_x, self.input_y):
                    self.selected_sprite = sprite
                    break 
            if self.selected_sprite:
                current_team = self.chess_board.get_current_team()
                piece = self.selected_sprite.piece
                role = chess.get_piece_role(piece)
                if chess.is_promotable_role(role):
                    promote_pawn = self.get_sprite_at(*self.selected_end)
                    new_piece = chess.role_as_team(role, current_team)
                    promote_pawn.piece = new_piece 
                    promote_pawn.tile = get_piece_tile(promote_pawn.piece)
                    self.play_sound('promote')
                    self.chess_board.set(*self.selected_end, chess.role_as_team(role, current_team))
                    #self.turn += 1
                    self.enter_state('wait')
                else:
                    self.play_sound('error')
            else:
                self.play_sound('error')

    def update_game_castle (self):
        assert self.state in ('queenside castle', 'kingside castle')
        assert self.selected_sprite and self.selected_start and self.selected_end
        assert None not in (self.moving_dx, self.moving_dy, self.moving_steps)
        assert self.castle_state in ('king', 'rook') 
        if self.moving_steps > 0:
            # Move the sprite a little
            self.moving_steps -= 1
            self.selected_sprite.x += self.moving_dx
            self.selected_sprite.y += self.moving_dy
        else:
            # Move on to move the castle/rook or finish all
            if self.castle_state == 'king':
                # Align king piece to grid
                self.move_sprite_on_board(self.selected_sprite, *self.selected_end)
                row = chess.get_king_row(self.chess_board.get_current_team())
                if self.state == 'kingside castle':
                    new_start = (row, 7)
                    new_end = (row, 5)
                elif self.state == 'queenside castle':
                    new_start = (row, 0)
                    new_end = (row, 3)
                else:
                    raise ValueError('not in correct castling state')
                self.selected_sprite = self.get_sprite_at(*new_start)
                self.castle_move_end = new_end # Note: variable only used below when aligning the rook to the board
                start_x, start_y = board_to_screen(*new_start)
                end_x, end_y = board_to_screen(*new_end)
                self.moving_steps = 4
                self.moving_dx = (end_x - start_x) // self.moving_steps
                self.moving_dy = (end_y - start_y) // self.moving_steps 
                self.castle_state = 'rook'
            elif self.castle_state == 'rook':
                # Align king piece to grid, using the extra attribute data
                self.move_sprite_on_board(self.selected_sprite, *self.castle_move_end) 
                # Now is when the chess board data is updated during castling
                self.play_sound('castle')
                self.chess_board.make_move(*self.selected_start, *self.selected_end)
                self.enter_state('wait')

    def update_game_mate (self): 
        # Wait to play the checkmate sound
        if self.sound_delay is not None:
            if self.sound_delay > 0:
                self.sound_delay -= 1
            else: 
                self.sound_delay = None
                self.create_highlight_sprites()
                self.play_sound('checkmate')
        # Check for the player to click on their king to resign
        if self.input_is_fresh:
            self.input_is_fresh = False
            if rowcol := screen_to_board(self.input_x, self.input_y):
                if sprite := self.get_sprite_at(*rowcol):
                    losing_king = self.chess_board.get_current_team()
                    if sprite.piece == losing_king:
                        self.enter_state('resign')

    def update_game_resign (self): 
        if self.move_steps > 0:
            self.move_steps -= 1
        else:
            self.play_sound('game over')
            self.enter_state('game over')

    def update_transition (self): 
        if self.move_steps > 0:
            self.move_steps -= 1
        else:
            self.enter_state('play')

    def update_menu (self):
        pass

    def update_game_over (self):
        if self.move_steps > 0:
            self.move_steps -= 1
        else:
            # Reset
            self.__init__(self.screen, self.spritesheet)

    def update (self):
        s = self.state
        if 'choose team' == s:
            self.update_game_choose() 
        elif 'wait' == s:
            self.update_game_wait()
        elif 'move' == s:
            self.update_game_move() 
        elif 'promote' == s:
            self.update_game_promote() 
        elif s in ('queenside castle', 'kingside castle'):
            self.update_game_castle()
        elif 'castle the rook' == s:
            self.update_game_castle_rook() 
        elif 'mate' == s:
            self.update_game_mate() 
        elif 'resign' == s:
            self.update_game_resign()
        elif 'transition' == s:
            self.update_transition()
        elif 'menu' == s:
            self.update_menu()
        elif 'game over' == s:
            self.update_game_over()
        else:
            raise ValueError('invalid game state: %s' %s) 

    def is_ai_turn (self):
        team = self.chess_board.get_current_team()
        return (team == chess.BLACK_KING and self.black_is_ai
                or team == chess.WHITE_KING and self.white_is_ai)

    def create_highlight_sprites (self):
        if self.state == 'mate':
            losing_king = self.chess_board.get_current_team()
            king_pos = self.chess_board.find_piece(losing_king)
            self.highlight_sprites = [Sprite(330, *board_to_screen(*king_pos), 2)]
        else:
            self.highlight_sprites = [Sprite(330, *board_to_screen(*self.selected_start), 2)]
            moves = self.chess_board.get_piece_moves(*self.selected_start)
            team = self.chess_board.get_current_team()
            for move in moves:
                if self.chess_board.is_legal_move(team, *self.selected_start, *move):
                    x, y = board_to_screen(*move)
                    sprite = Sprite(328, x, y, 2)
                    self.highlight_sprites.append(sprite)

    def draw_message (self, black=False): 
        offset = 318 if black else 0
        for sprite in self.message_sprites:
            draw_tile(self.screen, self.spritesheet, sprite.tile + offset, sprite.x, sprite.y) 

    def display (self):
        self.display_background()
        if self.is_play_state(self.state):
            # Highlighted squares
            for sprite in self.highlight_sprites:
                draw_tile(self.screen, self.spritesheet, sprite.tile, sprite.x, sprite.y, 2)
            # Game piece sprites
            for sprite in self.pieces:
                draw_tile(self.screen, self.spritesheet, sprite.tile, sprite.x, sprite.y, sprite.size)
            # Message character sprites
            self.draw_message()
            self.display_number(self.black_minutes, 104, 8)
            self.display_number(self.black_seconds, 128, 8)
            self.display_number(self.white_minutes, 104, 224)
            self.display_number(self.white_seconds, 128, 224)
            # Resignation closing circle
            if self.state == 'resign': 
                radius = self.move_steps * 4
                self.overlay_surf.fill((0, 0, 0))
                pygame.draw.circle(self.overlay_surf, (255, 255, 255), (self.target_x, self.target_y), radius)
                self.screen.blit(self.overlay_surf, (0, 0))
        elif self.state == 'game over':
            self.draw_message(black=True)
        elif self.state == 'menu':
            cursor = 257
            draw_tile(self.screen, self.spritesheet, cursor, 80, self.cursor_y)
        elif self.state == 'transition':
            tile = 316 + self.num_players 
            draw_tile(self.screen, self.spritesheet, tile, 72, 56)

    def set_background (self, array):
        self.background = array.copy()

    def display_background (self):
        for i, tile in enumerate(self.background):
            x = 8 * (i % 32)
            y = 8 * (i // 32)
            draw_tile(self.screen, self.spritesheet, tile, x, y)

    def get_sprite_at (self, row, col):
        for sprite in self.pieces:
            if sprite.row == row and sprite.col == col:
                return sprite

    def display_number (self, number, x, y):
        string = str(number)
        if len(string) < 2:
            string = '0' + string
        zero_tile = 284
        order = '0123______456789'
        for i, char in enumerate(string):
            tile = zero_tile + order.index(char)
            ix = x + i * 8
            draw_tile(self.screen, self.spritesheet, tile, ix, y) 
        
def get_sprite (spritesheet, sprite_id, sprite_size):
    x = 8 * (sprite_id % 32)
    y = 8 * (sprite_id // 32)
    size = sprite_size * 8
    return spritesheet.subsurface((x, y, size, size))

def get_piece_tile (piece):
    i = 20
    if chess.get_piece_team(piece) == chess.BLACK_KING:
        i += 64
    role = chess.get_piece_role(piece)
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

def display_init ():
    pygame.display.init()
    icon = pygame.image.load('icon.png')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Chess')
    return pygame.display.set_mode((SCALE * WIDTH, SCALE * HEIGHT))

def game_quit ():
    pygame.quit()

def char_to_tile (char):
    order = '$#abcdefghijklmnopqrstuvwxyz0123______456789-:!,.%@? _\''
    return 256 + order.index(char)

def main ():
    sys.setrecursionlimit(100)
    pygame.init()
    screen = display_init()
    spritesheet = pygame.image.load('spritesheet.png').convert_alpha()
    screen2 = pygame.Surface((WIDTH * SCALE, HEIGHT * SCALE))
    game = Game(screen, spritesheet)
    clock = pygame.time.Clock()
    while game.running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                break
            else:
                game.note_event(event)
        game.update()
        game.display()
        small = screen.subsurface((0, 0, WIDTH, HEIGHT))
        pygame.transform.scale(small, (WIDTH * SCALE, HEIGHT * SCALE), screen2)
        screen.blit(screen2, (0, 0))
        pygame.display.update()
    game_quit()

if __name__ == '__main__':
    main()
