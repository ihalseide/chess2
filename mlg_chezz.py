#!/usr/bin/env python3

import pygame
import chess

class ChessSprite (pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.rect = pygame.Rect(x, y, width, height)
        iw, ih = image.get_rect().size
        self.image = pygame.transform.scale(image, (iw*2, ih*2))

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
    size = 16 * 32
    square = 24 * 2
    offset = 8
    for i, piece in enumerate(chess_board):
        if piece != chess.EMPTY:
            x, y = chess_to_screen(corner_x, corner_y, i, square)
            x += offset
            y += offset
            coords = piece_to_sprite_coords(piece)
            img = spritesheet.subsurface(coords)
            ChessSprite(x, y, size, size, img, *groups)

def spawn_checkers (groups, spritesheet, corner_x, corner_y):
    size = 24
    for i in range(64):
        if chess.square_is_white(i):
            rect = (72, 0, size, size)
        else:
            rect = (48, 0, size, size)
        sprite = spritesheet.subsurface(rect)
        x, y = chess_to_screen(corner_x, corner_y, i, size * 2)
        ChessSprite(x, y, size * 2, size * 2, sprite, *groups)

def spawn_borders (groups, spritesheet, x0, y0):
    s = 16 * 2
    length = 24 * 2 * 8
    num_edges = 12
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
    for i in range(num_edges):
        ChessSprite(x0 + i * s, y0 - s, s, s,
                spritesheet.subsurface((16, 0, 16, 16)), *groups)
        ChessSprite(x0 + i * s, y0 + length, s, s,
                spritesheet.subsurface((16, 32, 16, 16)), *groups)
        ChessSprite(x0 - s, y0 + i * s, s, s,
                spritesheet.subsurface((0, 16, 16, 16)), *groups)
        ChessSprite(x0 + length, y0 + i * s, s, s,
                spritesheet.subsurface((32, 16, 16, 16)), *groups)

def spawn_board_labels(groups, spritesheet, corner_x, corner_y):
    size = 16
    square = 24 * 2
    for i in range(8):
        s1 = ChessSprite(corner_x + i * square + 8, corner_y + 8 * (square+1),
                size, size, spritesheet.subsurface((i * 16, 112, 16, 16)), *groups)
        s1.column = i
        s2 = ChessSprite(corner_x - square, corner_y + i * square + 8,
                size, size, spritesheet.subsurface((7*size - i * size, 96, size, size)), *groups)
        s2.row = i

def chess_to_screen (x0, y0, index, square_size):
    if index in range(64):
        x1 = x0 + (index % 8) * square_size
        y1 = y0 + (index // 8) * square_size
        return x1, y1
    else:
        return None

def screen_to_chess (x0, y0, x, y, square_size):
    x1 = (x - x0) // square_size
    y1 = (y - y0) // square_size
    if x1 in range(8) and y1 in range(8):
        return x1 + (y1 * 8)
    else:
        return None

def main ():
    pygame.init()
    pygame.display.init()
    icon = pygame.image.load('icon.png')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Chezz.exe')
    screen = pygame.display.set_mode((512, 512))

    clock = pygame.time.Clock()
    running = True

    board = chess.init_board()
    corner_x, corner_y = 64, 64
    hovered_row, hovered_column = None, None

    spritesheet = pygame.image.load('spritesheet.png').convert_alpha()
    all_sprites = pygame.sprite.Group()
    board_sprites = pygame.sprite.Group()
    piece_sprites = pygame.sprite.Group()
    label_sprites = pygame.sprite.Group()
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
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                i = screen_to_chess(corner_x, corner_y, x, y, 2*24)
                if i in range(64):
                    hovered_column = i % 8
                    hovered_row = i // 8
                else:
                    hovered_row = hovered_column = None

        screen.fill((120, 120, 120))
        board_sprites.draw(screen)
        piece_sprites.draw(screen)
        label_sprites.draw(screen)

        pygame.draw.rect(screen, (255,0,255), (corner_x-2,corner_y-2,4,4))
        pygame.display.update()

if __name__ == '__main__':
    main()
