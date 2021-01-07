#!/usr/bin/env python3

import pygame
import chess

class ChessSprite (pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image

def piece_to_sprite_coords (piece):
    role = chess.piece_role(piece)
    allegiance = chess.piece_allegiance(piece)
    role_order = [chess.WHITE_PAWN, chess.WHITE_BISHOP, chess.WHITE_KNIGHT,
            chess.WHITE_ROOK, chess.WHITE_QUEEN, chess.WHITE_KING]
    x = role_order.index(role) * 16 
    if allegiance == chess.WHITE_KING:
        y = 80
    else:
        y = 64
    return (x, y, 16, 16)

def spawn_pieces (groups, spritesheet, corner_x, corner_y, chess_board):
    for i, piece in enumerate(chess_board):
        if piece != chess.EMPTY:
            x, y = chess_to_screen(corner_x, corner_y, i, 32)
            x += 8
            y += 8
            coords = piece_to_sprite_coords(piece)
            img = spritesheet.subsurface(coords)
            ChessSprite(x, y, 16, 16, img, *groups)

def spawn_checkers (groups, spritesheet, corner_x, corner_y):
    size = 32
    for i in range(64):
        if chess.square_is_white(i):
            rect = (80, 0, 32, 32)
        else:
            rect = (48, 0, 32, 32)
        sprite = spritesheet.subsurface(rect)
        x, y = chess_to_screen(corner_x, corner_y, i, size)
        ChessSprite(x, y, size, size, sprite, *groups)

def spawn_borders (groups, spritesheet, x0, y0):
    s = 16
    length = 32 * 8
    # Corners
    ChessSprite(x0 - s, y0 - s, s, s,
            spritesheet.subsurface((0, 0, 16, 16)), *groups)
    ChessSprite(x0 - s, y0 + length, s, s,
            spritesheet.subsurface((0, 32, 16, 16)), *groups)
    ChessSprite(x0 + length, y0 - s, s, s,
            spritesheet.subsurface((32, 0, 16, 16)), *groups)
    ChessSprite(x0 + length, y0 + length, s, s,
            spritesheet.subsurface((32, 32, 16, 16)), *groups)
    # Edges
    for i in range(16):
        ChessSprite(x0 + i * s, y0 - s, s, s,
                spritesheet.subsurface((16, 0, 16, 16)), *groups)
        ChessSprite(x0 + i * s, y0 + length, s, s,
                spritesheet.subsurface((16, 32, 16, 16)), *groups)
        ChessSprite(x0 - s, y0 + i * s, s, s,
                spritesheet.subsurface((0, 16, 16, 16)), *groups)
        ChessSprite(x0 + length, y0 + i * s, s, s,
                spritesheet.subsurface((32, 16, 16, 16)), *groups)

def spawn_board_labels(groups, spritesheet, corner_x, corner_y):
    for i in range(8):
        ChessSprite(corner_x + i * 32 + 8, corner_y + 8 * 33, 16, 16,
                spritesheet.subsurface((i * 16, 112, 16, 16)), *groups)
        ChessSprite(corner_x - 24, corner_y + i * 32 + 8, 16, 16,
                spritesheet.subsurface((7*16 - i * 16, 96, 16, 16)), *groups)

def chess_to_screen (x0, y0, index, square_size):
    x1 = x0 + (index % 8) * square_size
    y1 = y0 + (index // 8) * square_size
    return x1, y1

def screen_to_chess (x0, y0, x, y, square_size):
    x1 = (x - x0) // square_size
    y1 = (y - y0) // square_size
    return x1 + (y1 * 8)

def main ():
    pygame.init()
    screen = pygame.display.set_mode((512, 512))
    pygame.display.set_caption('chess.exe')
    clock = pygame.time.Clock()
    running = True
    board = chess.init_board()
    spritesheet = pygame.image.load('spritesheet.png').convert_alpha()
    all_sprites = pygame.sprite.Group()
    board_sprites = pygame.sprite.Group()
    piece_sprites = pygame.sprite.Group()
    label_sprites = pygame.sprite.Group()
    corner_x, corner_y = 128, 128
    spawn_checkers([all_sprites, board_sprites], spritesheet, corner_x, corner_y)
    spawn_borders([all_sprites, board_sprites], spritesheet, corner_x, corner_y)
    spawn_board_labels([all_sprites, label_sprites], spritesheet, corner_x, corner_y)
    spawn_pieces([all_sprites, piece_sprites], spritesheet, corner_x, corner_y, board)
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass
        screen.fill((120, 120, 120))
        board_sprites.draw(screen)
        piece_sprites.draw(screen)
        label_sprites.draw(screen)
        pygame.display.update()

if __name__ == '__main__':
    main()
