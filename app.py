#!/usr/bin/env python3

import pygame
import chess

def draw_checkers (screen, x, y, size, dark_color, light_color):
    for i in range(64):
        if chess.square_is_white(i):
            color = light_color
        else:
            color = dark_color
        x1, y1 = chess_to_screen(x, y, i, size)
        pygame.draw.rect(screen, color, (x1, y1, size, size))

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
    screen = pygame.display.set_mode((540, 540))
    pygame.display.set_caption('chess.exe')
    clock = pygame.time.Clock()
    running = True
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
        draw_checkers(screen, 100, 100, 24, (20,20,20), (235,235,235))
        pygame.display.update()

if __name__ == '__main__':
    main()
