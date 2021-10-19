#!/usr/bin/env python3 

import pygame, os, threading, random
import chess, chess_ai
from backgrounds import *

AI_TIME_LIMIT = 3000000000 # nanoseconds
FPS = 30 # Frames per Second

WIDTH, HEIGHT = 800, 600 # px
SPRITE_TILE_SIZE = 16 # px

BOARD_GRID_SIZE = 32 # px
BOARD_X, BOARD_Y = (WIDTH - 8 * BOARD_GRID_SIZE)//2, 176 # px

JAIL_START_X = BOARD_X # px
JAIL_END_X = BOARD_X + 8 * BOARD_GRID_SIZE # px
BLACK_JAIL_Y = BOARD_Y + (9 * BOARD_GRID_SIZE) # px
WHITE_JAIL_Y = BOARD_Y - 2 * BOARD_GRID_SIZE # px

GAME_OVER_TEXT = (
        'All your base are belong to us',
        'All your king are belong to us',
        'All your square are belong to us',
        'Free play unlocked',
        'I\'ll be back',
        'I\'m king of the world',
        'You can now play as Luigi',
        'You can run but you can\'t hide',
        )

SOUND_NAMES = (
    'check',
    'checkmate',
    'error',
    'move',
    'promote',
    'can promote',
    'capture',
    'castle',
    'resign',
    'reveal',
    'game over'
)

class Sprite:
    def __init__(self, image, x, y, size=1):
        self.image = image
        self.x = x
        self.y = y
        self.size = size

class AutoPlayer (threading.Thread):
    def __init__ (self, chess_board, time_limit):
        threading.Thread.__init__(self)
        self.chess_board = chess_board
        self.time_limit = time_limit
        self.result = None
        self.depth = None

    def run (self):
        self.result, self.depth = chess_ai.ai_process(self.chess_board, self.time_limit)


class Game:
    valid_states = (
        'menu',
        'transition',
        'play',
        'wait',
        'move',
        'promote',
        'queenside castle',
        'kingside castle',
        'mate',
        'resign',
        'choose team',
        'game over'
    )

    play_states = (
        'play',
        'wait',
        'move',
        'promote',
        'queenside castle', 
        'kingside castle',
        'mate',
        'castle the rook',
        'resign',
        'choose team'
    )

    def __init__ (self, screen, spritesheet):
        self.screen = screen
        self.spritesheet = spritesheet

        self.running = True
        self.debug = False
        self.done = False
        self.num_players = None
        self.pieces = None
        self.theme = 2
        assert self.theme in range(3)

        self.message_x, self.message_y = 100, 20
        self.message = ''

        self.init_textures()
        self.init_sounds()

        self.init_chess()

        self.enter_state('menu')

    def create_background(self, array):
        new_surf = pygame.Surface((WIDTH, HEIGHT))
        surf_width = WIDTH // SPRITE_TILE_SIZE

        for i, tile_id in enumerate(array):
            x = SPRITE_TILE_SIZE * (i % surf_width)
            y = SPRITE_TILE_SIZE * (i // surf_width)
            img = self.get_sprite_at(y, x)
            new_surf.blit(img, (x, y))

        return new_surf


    def init_textures (self): 
        self.menu_background = self.create_background(MENU_BACKGROUND)
        self.transition_background = self.create_background(TRANSITION_BACKGROUND)
        self.game_background = self.create_background(GAME_BACKGROUND)

        self.text_surface = self.spritesheet.subsurface((0, 240, 256, 16))
        self.text_surface.set_colorkey((0, 0, 0)) # black
        self.message_surface = self.create_text('chess', 160, 10) 


    def is_play_state (self, state):
        return state in self.play_states


    def init_chess (self): 
        self.chess_board = chess.Game()
        self.black_is_ai = False
        self.white_is_ai = False
        self.ai_thread = None

    
    def get_message (self):
        assert self.state in self.valid_states
        is_white = self.chess_board.get_current_team() == chess.WHITE_KING
        state = self.state

        if self.theme == 1:
            if is_white:
                name = 'USSR'
            else:
                name = 'USA'
        else:
            if is_white:
                name = 'white'
            else:
                name = 'black'

        if 'game over' == state:
            return random.choice(GAME_OVER_TEXT)
        if 'choose team' == state:
            return 'select the pieces to lead' 
        elif 'promote' == state:
            return '%s pawn promotion' % name
        elif 'mate' == state or 'resign' == state:
            if self.chess_winner in (chess.WHITE_KING, chess.BLACK_KING):
                return 'checkmate'
            else:
                return 'stalemate'
        elif 'wait' == state:
            if self.chess_board.move_num == 0:
                return '%s moves first' % name
            elif self.chess_board.is_king_in_check(self.chess_board.get_current_team()):
                return '%s is in check' % name
            else:
                return '%s to move' % name
        else:
            return ''


    def update_message (self):
        message = self.get_message() 
        if message != self.message:
            self.message = message
            self.message_surface = self.create_text(message, width=200, height=100)


    def create_text (self, text, width, height):
        surf = pygame.Surface((width, height))
        surf.set_colorkey((0, 0, 0))
        self.draw_text(surf, text, 0, 0, width, height) 
        return surf


    def init_sounds (self):
        sound = lambda name: pygame.mixer.Sound(os.path.join('sound', name))
        self.sounds = {name: sound(name + '.wav') for name in SOUND_NAMES}


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
            self.background = self.menu_background
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
            self.background = self.transition_background
            self.init_movement()
            self.init_chess()
            self.init_timers()
            self.init_capturing_area()
            self.init_pieces()
            self.highlight_sprites = []
            self.update_message()
        elif state == 'play':
            self.background = self.game_background
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
            king_square = self.chess_board.find_king(team)
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
            losing_coords = self.chess_board.find_king(losing_king)
            king_sprite = self.get_sprite_at(*losing_coords)
            self.target_x, self.target_y = king_sprite.x + 8, king_sprite.y + 8
        elif state == 'game over': 
            self.move_steps = 180 
            self.play_sound('game over')
            self.background = self.transition_background
            self.update_message()
        else:
            # If this point is reached, there is a typo in the above IF statements
            raise SyntaxError() 

    def init_pieces (self):
        self.pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.chess_board.get(row, col)
                if piece != chess.EMPTY:
                    rect = self.get_piece_spot(piece)
                    image = self.spritesheet.subsurface(rect)
                    x, y = board_to_screen(row, col)
                    new = Sprite(image, x, y, size=2)
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
                xy = event.pos
                if self.trigger_option_0_rect.collidepoint(xy):
                    if not self.show_option_0:
                        self.play_sound('reveal')
                    self.show_option_0 = True
                elif self.show_option_0 and self.option_0_rect.collidepoint(xy):
                    self.num_players = 0
                elif self.option_1_rect.collidepoint(xy):
                    self.num_players = 1
                elif self.option_2_rect.collidepoint(xy):
                    self.num_players = 2
                elif not self.debug and (xy[0] == xy[1] == 0):
                    self.play_sound('reveal')
                    self.debug = True
                if self.num_players is not None:
                    self.enter_state('transition')
            elif event.type == pygame.MOUSEMOTION:
                xy = event.pos
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
                self.input_x, self.input_y = event.pos
                self.input_is_fresh = True

    def move_sprite_on_board (self, sprite, row, col):
        assert row in range(8) and col in range(8)
        sprite.row, sprite.col = row, col
        x, y = board_to_screen(row, col)
        sprite.x, sprite.y = x, y

    def remove_sprite (self, sprite):
        delta = 32

        sprite.row = None
        sprite.col = None

        if chess.get_piece_team(sprite.piece) == chess.WHITE_KING:
            sprite.x = self.white_jail_x
            sprite.y = self.white_jail_y
            self.white_jail_x += delta
            if self.white_jail_x >= JAIL_END_X:
                self.white_jail_x = JAIL_START_X
                self.white_jail_y -= delta
        else:
            sprite.x = self.black_jail_x
            sprite.y = self.black_jail_y
            self.black_jail_x += delta
            if self.black_jail_x >= JAIL_END_X:
                self.black_jail_x = JAIL_START_X
                self.black_jail_y += delta

    def update_timers (self): 
        # Don't time before the first move is made by white
        if self.chess_board.move_num == 0:
            return

        if self.chess_board.get_current_team() == chess.BLACK_KING:
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


    def update_game_wait_ai (self):
        if self.ai_thread is not None:
            if not self.ai_thread.is_alive():
                row, col, to_row, to_col = self.ai_thread.result
                print('ai depth reached:', self.ai_thread.depth)
                self.selected_start = row, col
                self.selected_end = to_row, to_col 
                self.selected_sprite = self.get_sprite_at(*self.selected_start)
                self.ai_thread = None
        else:
            # Startup AI eval
            self.ai_thread = AutoPlayer(self.chess_board.copy(), AI_TIME_LIMIT)
            self.ai_thread.start()

    def update_game_wait_player (self):
        if self.input_is_fresh:
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


    def update_game_wait (self): 
        # Validate selection of pieces and moves
        self.update_timers() 
        if self.is_ai_turn():
            self.update_game_wait_ai()
        else:
            self.update_game_wait_player()

        if self.selected_start and self.selected_end:
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
                    rect = self.get_piece_spot(promote_pawn.piece)
                    promote_pawn.image = self.spritesheet.subsurface(rect)
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
            self.enter_state('game over')


    def update_transition (self): 
        if self.move_steps > 0:
            self.move_steps -= 1
        else:
            self.enter_state('play')


    def update_game_over (self):
        if self.move_steps > 0:
            self.move_steps -= 1
        else:
            self.done = True


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
            pass
        elif 'game over' == s:
            self.update_game_over()
        else:
            raise ValueError('invalid game state: %s' %s) 


    def is_ai_turn (self):
        team = self.chess_board.get_current_team()
        return (team == chess.BLACK_KING and self.black_is_ai
                or team == chess.WHITE_KING and self.white_is_ai)


    def create_highlight_sprites (self):
        solid_x, solid_y = (224, 80)
        solid = self.spritesheet.subsurface((solid_x, solid_y, 32, 32))
        circle_x, circle_y = (192, 80)
        circle = self.spritesheet.subsurface((circle_x, circle_y, 32, 32))

        if self.state == 'mate':
            losing_king = self.chess_board.get_current_team()
            king_pos = self.chess_board.find_king(losing_king)
            self.highlight_sprites = [Sprite(solid, *board_to_screen(*king_pos), 2)]
        else:
            self.highlight_sprites = [Sprite(solid, *board_to_screen(*self.selected_start), 2)]
            team = self.chess_board.get_current_team()
            for move in self.chess_board.get_legal_piece_moves(*self.selected_start):
                x, y = board_to_screen(*move)
                sprite = Sprite(circle, x, y, 2)
                self.highlight_sprites.append(sprite)


    def draw_message (self, black=False): 
        self.screen.blit(self.message_surface, (self.message_x, self.message_y))


    def display (self):
        self.screen.blit(self.background, (0, 0))
        if self.is_play_state(self.state):
            # Highlighted squares
            for sprite in self.highlight_sprites:
                self.screen.blit(sprite.image, (sprite.x, sprite.y))
            # Game piece sprites
            for sprite in self.pieces:
                self.screen.blit(sprite.image, (sprite.x, sprite.y))
            # Message character sprites
            self.draw_message()
            self.draw_text(self.screen, str(self.black_minutes), 104, 32)
            self.draw_text(self.screen, str(self.black_seconds), 128, 32)
            self.draw_text(self.screen, str(self.white_minutes), 104, 216)
            self.draw_text(self.screen, str(self.white_seconds), 128, 216)
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
            #self.draw_tile(self.screen, cursor, 80, self.cursor_y)
        elif self.state == 'transition':
            #tile = 316 + self.num_players 
            #self.draw_tile(self.screen, tile, 72, 56)
            pass


    def get_sprite_at (self, row, col):
        for sprite in self.pieces:
            if sprite.row == row and sprite.col == col:
                return sprite


    def char_to_tile (self, char):
        order = 'abcdefghijklmnopqrstuvwxyz0123456789-:!,.%@? _\''
        i = order.index(char.lower())
        x = (i * 8) % 256
        y = 8 * (i // 32)
        return self.text_surface.subsurface((x, y, 8, 8))


    def draw_text (self, surf, text, x0, y0, x1, y1):
        x, y = x0, y0
        x_space, y_space = 8, 16

        for char in text:
            if x > x1 - x_space:
                x = x0
                y += y_space
                if y > y1 - y_space:
                    # Boundary is completely exceeded
                    break

            tile = self.char_to_tile(char)
            surf.blit(tile, (x, y))
            x += x_space 

        return (x, y)


    def get_piece_spot (self, piece):
        order = (chess.WHITE_PAWN, chess.WHITE_BISHOP, chess.WHITE_KNIGHT,
                chess.WHITE_ROOK, chess.WHITE_QUEEN, chess.WHITE_KING)

        team = chess.get_piece_team(piece)
        role = chess.get_piece_role(piece)
        col = order.index(role)

        # Theme #0 has smaller sprites than the others
        if self.theme == 0:
            row = 4
            size = 16
        else:
            col *= 2
            row = 5 + (self.theme - 1) * 4
            size = 32

        if team == chess.BLACK_KING:
            # Theme #0 has sprites on the same row
            if self.theme == 0:
                col += 6
            else:
                row += 2
                
        result = (col * 16, row * 16, size, size)
        return result


def screen_to_board (x, y):
    col = (x - BOARD_X) // BOARD_GRID_SIZE
    row = (y - BOARD_Y) // BOARD_GRID_SIZE
    if (col in range(8)) and (row in range(8)):
        return (row, col)


def board_to_screen (row, col):
    if (col in range(8)) and (row in range(8)):
        x = BOARD_X + col * BOARD_GRID_SIZE
        y = BOARD_Y + row * BOARD_GRID_SIZE
        return (x, y)


def main ():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    icon = pygame.image.load('icon.ico')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Chezz')

    spritesheet = pygame.image.load('textures.png').convert_alpha()

    game = Game(screen, spritesheet)
    clock = pygame.time.Clock()

    while game.running:
        if game.done:
            # Reset the game
            game = Game(screen, spritesheet)
        clock.tick(FPS)
        for event in pygame.event.get():
            game.note_event(event)
            if event.type == pygame.QUIT:
                game.running = False
                break
        game.update()
        game.display()
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
