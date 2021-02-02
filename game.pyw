#!/usr/bin/env python3

import pygame
import chess
import os

WIDTH, HEIGHT = 256, 240
SCALE = 2
FPS = 30 # Frames Per Seconds
CORNER_X, CORNER_Y = 64, 56
GRID_SIZE = 16
MESSAGE_X, MESSAGE_Y = 40, 32 
JAIL_START_X, JAIL_END_X = 200, 248
BLACK_JAIL_Y = 200
WHITE_JAIL_Y = 40
WIN_TEXT = [
        "you can now play as luigi",
        "free play unlocked"
        ]
LOSE_TEXT = [
        "all your base are belong to us",
        "sorry mate",
        "screams echo around you"
        ]
MENU_BACKGROUND = [ 
        288,289,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,292,293,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,325,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,357,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,389,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,0,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,19,308,308,308,308,308,421,
        320,308,308,308,308,308,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,179,308,308,308,308,308,421,
        320,308,308,308,308,308,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,211,308,308,308,308,308,421,
        320,308,308,308,308,308,32,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,179,308,308,308,308,308,421,
        320,308,308,308,308,308,64,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,211,308,308,308,308,308,421,
        320,308,308,308,308,308,32,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,308,308,308,308,308,421,
        320,308,308,308,308,308,64,193,33,193,194,193,194,193,194,193,194,193,194,193,194,193,194,193,194,211,308,308,308,308,308,421,
        320,308,308,308,308,308,224,225,226,225,226,225,226,225,226,225,226,225,226,225,226,225,226,225,226,243,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,285,308,273,269,258,282,262,275,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,286,308,273,269,258,282,262,275,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        352,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        384,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        416,308,308,308,308,308,308,306,286,284,286,285,308,266,283,258,268,308,265,258,269,276,262,266,261,262,308,308,308,308,308,421,
        448,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,450,451,451,452,453
        ]
MENU_BACKGROUND_2 = [
        288,289,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,292,293,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,325,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,357,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,389,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,0,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,19,308,308,308,308,308,421,
        320,308,308,308,308,308,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,179,308,308,308,308,308,421,
        320,308,308,308,308,308,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,211,308,308,308,308,308,421,
        320,308,308,308,308,308,32,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,179,308,308,308,308,308,421,
        320,308,308,308,308,308,64,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,211,308,308,308,308,308,421,
        320,308,308,308,308,308,32,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,308,308,308,308,308,421,
        320,308,308,308,308,308,64,193,33,193,194,193,194,193,194,193,194,193,194,193,194,193,194,193,194,211,308,308,308,308,308,421,
        320,308,308,308,308,308,224,225,226,225,226,225,226,225,226,225,226,225,226,225,226,225,226,225,226,243,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,284,308,273,269,258,282,262,275,307,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,285,308,273,269,258,282,262,275,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,286,308,273,269,258,282,262,275,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        320,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        352,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        384,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,421,
        416,308,308,308,308,308,308,306,286,284,286,285,308,266,283,258,268,308,265,258,269,276,262,266,261,262,308,308,308,308,308,421,
        448,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,449,450,451,451,452,453 
        ]
TRANSITION_BACKGROUND = [ 
        513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,
        513,480,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,481,482,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,326,513,498,494,483,507,487,500,513,489,483,495,487,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,494,487,502,513,502,490,487,513,489,483,495,487,501,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,484,487,489,491,496,517,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,512,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,514,513,
        513,544,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,545,546,513,
        513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513,513
        ]
GAME_BACKGROUND = [
        308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,
        308,259,269,258,260,268,256,308,277,266,270,262,308,308,308,301,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,288,289,290,290,290,290,290,290,290,290,290,290,290,290,290,290,290,293,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,325,308,308,308,308,308,308,308,
        308,308,308,308,308,308,298,320,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,357,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,320,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,389,308,308,308,308,308,308,308,
        308,308,308,308,308,308,297,320,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,296,320,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,320,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,295,320,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,294,320,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,320,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,287,320,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,320,321,322,323,324,321,322,323,324,321,322,323,324,321,322,323,324,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,286,352,353,354,355,356,353,354,355,356,353,354,355,356,353,354,355,356,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,384,385,386,387,388,385,386,387,388,385,386,387,388,385,386,387,388,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,285,416,417,418,419,420,417,418,419,420,417,418,419,420,417,418,419,420,421,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,448,449,449,449,449,449,449,449,449,449,449,449,449,449,450,451,452,453,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,308,258,308,259,308,260,308,261,308,262,308,263,308,264,308,265,308,308,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,
        308,280,265,266,277,262,257,308,277,266,270,262,308,308,308,301,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,
        308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308,308
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
        self.state = 'menu'
        self.init_sounds()
        self.init_menu()

    def init_menu (self):
        self.background = MENU_BACKGROUND
        self.num_players = None
        self.show_option_0 = False
        self.trigger_option_0_rect = pygame.Rect(72, 224, 8, 8)
        self.option_0_rect = pygame.Rect(96, 120, 64, 8)
        self.option_1_rect = pygame.Rect(96, 136, 64, 8)
        self.option_2_rect = pygame.Rect(96, 152, 64, 8)
        self.cursor_y = 256

    def init_transition (self): 
        self.transition_timer = 90
        self.state = 'transition'
        self.background = TRANSITION_BACKGROUND

    def set_game (self): 
        self.background = GAME_BACKGROUND
        self.state = 'play'

    def init_game (self):
        self.init_movement()
        self.init_chess()
        self.init_timers()
        self.init_capturing_area()
        self.init_pieces()
        self.highlight_sprites = []
        self.enter_game_state('wait')
        self.init_message()

    def init_chess (self): 
        self.chess_board = chess.Board()
        self.turn = 0
        self.is_check = False

    def init_message (self):
        self.message = None
        self.message_sprites = []
        self.update_message()
    
    def update_message (self):
        is_white = chess.get_current_team(self.turn) == chess.WHITE_KING
        state = self.game_state
        if state == 'promote':
            if is_white:
                message = 'white# pawn promotion'
            else:
                message = 'black$ pawn promotion'
        elif state == 'checkmate':
            winner = self.chess_board.get_winner()
            if winner == chess.WHITE_KING:
                message = 'white# checkmates black$!'
            elif winner == chess.BLACK_KING:
                message = 'black$ checkmates white#!'
        elif state == 'wait':
            if is_white:
                if self.is_check:
                    message = 'white# is in check'
                elif self.turn == 0:
                    message = 'white# to make 1st move'
                else:
                    message = 'white# to move'
            else:
                if self.is_check:
                    message = 'black$ is in check'
                else:
                    message = 'black$ to move'
        else:
            message = self.message

        if message != self.message:
            self.message = message
            self.message_sprites = []
            for i, char in enumerate(self.message):
                tile = char_to_tile(char)
                s = Sprite(tile, MESSAGE_X + i * 8, MESSAGE_Y, 1)
                self.message_sprites.append(s)

    def init_sounds (self):
        s = lambda name: pygame.mixer.Sound(os.path.join('sound', name))
        self.sounds = {
                'check': s('check.wav'),
                'checkmate': s('checkmate.wav'),
                'error': s('error.wav'),
                'move': s('move.wav'),
                'promote': s('promote.wav'),
                'can promote': s('can promote.wav'),
                'capture': s('capture.wav'),
                'castle': s('castle.wav'),
                'resign': s('resign.wav'),
                'reveal': s('reveal.wav')
                }

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
        # State:
        self.game_state = None
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

    def update_check (self): 
        team = chess.get_current_team(self.turn + 1)
        self.is_check = self.chess_board.king_is_in_check(team)

    def enter_game_state (self, state):
        # print(self.game_state, '--->', state)
        valid_states = ('wait', 'move', 'promote', 'queenside castle', 'kingside castle', 'checkmate', 'castle the rook', 'resign')
        assert state in valid_states
        if state == 'wait':
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
            self.update_check()
            if winner := self.chess_board.get_winner():
                self.enter_game_state('checkmate')
                return # don't increase the turn counter

        elif state == 'move':
            assert self.selected_sprite and self.selected_start and self.selected_end
            start_x, start_y = board_to_screen(*self.selected_start)
            end_x, end_y = board_to_screen(*self.selected_end)
            self.moving_steps = 8
            self.moving_dx = (end_x - start_x) // self.moving_steps
            self.moving_dy = (end_y - start_y) // self.moving_steps

        elif state == 'promote':
            assert self.selected_sprite and self.selected_start and self.selected_end 

        elif state in ('queenside castle', 'kingside castle'):
            assert self.selected_sprite and self.selected_start and self.selected_end

            team = chess.get_current_team(self.turn)
            can_castle = (
                    (state == 'kingside castle' and self.chess_board.can_kingside_castle(team))
                    or
                    (state == 'queenside castle' and self.chess_board.can_queenside_castle(team)))
            if can_castle:
                start_x, start_y = board_to_screen(*self.selected_start)
                end_x, end_y = board_to_screen(*self.selected_end)
                self.moving_steps = 4
                self.moving_dx = (end_x - start_x) // self.moving_steps
                self.moving_dy = (end_y - start_y) // self.moving_steps
            else:
                self.play_sound('error')
                self.enter_game_state('wait')

        elif state ==  'castle the rook':
            self.previous_castle_state = self.game_state
            assert self.previous_castle_state in ('queenside castle', 'kingside castle')

            if chess.get_current_team(self.turn) == chess.BLACK_KING:
                row = 0
            else:
                row = 7

            if self.previous_castle_state == 'kingside castle':
                self.selected_start = (row, 7)
                self.selected_end = (row, 5)
            elif self.previous_castle_state == 'queenside castle':
                self.selected_start = (row, 0)
                self.selected_end = (row, 3)
            self.selected_sprite = self.get_sprite_at(*self.selected_start)

            start_x, start_y = board_to_screen(*self.selected_start)
            end_x, end_y = board_to_screen(*self.selected_end)
            self.moving_steps = 4
            self.moving_dx = (end_x - start_x) // self.moving_steps
            self.moving_dy = (end_y - start_y) // self.moving_steps

        elif state == 'checkmate':
            self.sound_delay = 16

        elif state == 'resign':
            self.move_steps = 32
            self.play_sound('resign')

        else:
            # If this point is reached, I made a typo in the above
            # if-statements
            raise SyntaxError()

        self.game_state = state

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
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos[0] // SCALE, event.pos[1] // SCALE
            if self.state == 'play':
                self.input_x = x
                self.input_y = y
                self.input_is_fresh = True
            elif self.state == 'menu':
                xy = x,y
                if self.trigger_option_0_rect.collidepoint(xy):
                    if not self.show_option_0:
                        self.background = MENU_BACKGROUND_2
                        self.play_sound('reveal')
                    self.show_option_0 = True
                elif self.show_option_0 and self.option_0_rect.collidepoint(xy):
                    self.num_players = 0
                elif self.option_1_rect.collidepoint(xy):
                    self.num_players = 1
                elif self.option_2_rect.collidepoint(xy):
                    self.num_players = 2
                if self.num_players is not None:
                    self.init_game()
                    self.init_transition()
            elif self.state == 'transition':
                pass
            else:
                raise SyntaxError('bad state')
        elif event.type == pygame.MOUSEMOTION:
            x, y = event.pos[0] // SCALE, event.pos[1] // SCALE
            if self.state == 'menu':
                xy = x,y
                if self.show_option_0 and self.option_0_rect.collidepoint(xy):
                    self.cursor_y = 120
                elif self.option_1_rect.collidepoint(xy):
                    self.cursor_y = 136
                elif self.option_2_rect.collidepoint(xy):
                    self.cursor_y = 152 

    def move_sprite_on_board (self, sprite, row, col):
        assert row in range(8) and col in range(8)
        sprite.row, sprite.col = row, col
        x, y = board_to_screen(row, col)
        sprite.x, sprite.y = x, y

    def remove_sprite (self, sprite):
        sprite.row = None
        sprite.col = None
        if chess.piece_team(sprite.piece) == chess.WHITE_KING:
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

    def update (self):
        self.clock.tick(FPS)
        if self.state == 'menu':
            pass
        elif self.state == 'play':
            self.update_game()
        elif self.state == 'transition':
            if self.transition_timer > 0:
                self.transition_timer -= 1
            else:
                self.set_game()

    def update_timers (self): 
        # Don't update the timer until white has moved first
        if self.turn > 0 and self.game_state != 'checkmate':
            if chess.get_current_team(self.turn) == chess.BLACK_KING:
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

    def update_game (self):
        if self.game_state == 'wait':
            # Validate selection of pieces and moves
            if self.input_is_fresh:
                self.input_is_fresh = False
                rowcol = screen_to_board(self.input_x, self.input_y)
                if rowcol:
                    current_team = chess.get_current_team(self.turn)
                    sprite = self.get_sprite_at(*rowcol)
                    is_team_mate = (sprite is not None) and (current_team == chess.piece_team(sprite.piece))
                    if is_team_mate:
                            self.selected_start = rowcol
                            self.create_highlight_sprites()
                    else:
                        if self.selected_start:
                            self.selected_end = rowcol
                        else:
                            self.play_sound('error')
                            self.enter_game_state('wait')
                else:
                    # Clicking off of the board --> deselect everything
                    self.enter_game_state('wait')
            if self.selected_start:
                self.create_highlight_sprites()
                if self.selected_end:
                    # Validate start of selection
                    self.selected_sprite = self.get_sprite_at(*self.selected_start) # could be None
                    target_sprite = self.get_sprite_at(*self.selected_end) # could be None
                    current_team = chess.get_current_team(self.turn)
                    is_legal_move = self.chess_board.is_legal_move(current_team, *self.selected_start, *self.selected_end)
                    if is_legal_move:
                        self.enter_game_state('move')
                    elif self.is_move_queenside_castle(*self.selected_start, *self.selected_end) and self.chess_board.can_queenside_castle(current_team):
                        self.enter_game_state('queenside castle')
                    elif self.is_move_kingside_castle(*self.selected_start, *self.selected_end) and self.chess_board.can_kingside_castle(current_team):
                        self.enter_game_state('kingside castle')
                    else:
                        self.play_sound('error')
                        self.enter_game_state('wait')
        elif self.game_state == 'move':
            assert self.selected_sprite and self.selected_start and self.selected_end
            assert None not in (self.moving_dx, self.moving_dy, self.moving_steps)
            if self.moving_steps > 0:
                # Move the sprite a little
                self.moving_steps -= 1
                self.selected_sprite.x += self.moving_dx
                self.selected_sprite.y += self.moving_dy
            else:
                # Remove the captured sprite (if any)
                target = self.get_sprite_at(*self.selected_end) 
                if target:
                    self.remove_sprite(target)
                # Finalize the moving sprite
                self.move_sprite_on_board(self.selected_sprite, *self.selected_end)
                # Update the chess board
                self.chess_board.move(*self.selected_start, *self.selected_end)
                if self.chess_board.is_promotable(*self.selected_end):
                    self.play_sound('can promote')
                    self.enter_game_state('promote')
                else:
                    self.update_check()
                    if self.is_check:
                        self.play_sound('check')
                    else:
                        if target: 
                            self.play_sound('capture')
                        else:
                            self.play_sound('move')
                    self.turn += 1
                    self.enter_game_state('wait')

        elif self.game_state == 'promote':
            if self.input_is_fresh:
                self.input_is_fresh = False
                self.selected_sprite = None
                for sprite in self.pieces:
                    rect = pygame.Rect(sprite.x, sprite.y, 16, 16)
                    if rect.collidepoint(self.input_x, self.input_y):
                        self.selected_sprite = sprite
                        break 
                if self.selected_sprite:
                    current_team = chess.get_current_team(self.turn)
                    piece = self.selected_sprite.piece
                    role = chess.piece_role(piece)
                    if chess.is_promotable_role(role):
                        promote_pawn = self.get_sprite_at(*self.selected_end)
                        new_piece = chess.role_as_team(role, current_team)
                        promote_pawn.piece = new_piece 
                        promote_pawn.tile = get_piece_tile(promote_pawn.piece)
                        self.play_sound('promote')
                        self.chess_board.promote(current_team, *self.selected_end, role)
                        self.turn += 1
                        self.enter_game_state('wait')
                    else:
                        self.play_sound('error')
                else:
                    self.play_sound('error')

        elif self.game_state in ('queenside castle', 'kingside castle'):
            assert self.selected_sprite and self.selected_start and self.selected_end
            assert None not in (self.moving_dx, self.moving_dy, self.moving_steps)
            assert chess.piece_role(self.selected_sprite.piece) == chess.WHITE_KING
            if self.moving_steps > 0:
                # Move the sprite (KING) a little
                self.moving_steps -= 1
                self.selected_sprite.x += self.moving_dx
                self.selected_sprite.y += self.moving_dy
            else:
                # Align king to grid
                self.move_sprite_on_board(self.selected_sprite, *self.selected_end)
                # Now start moving the rook
                self.enter_game_state('castle the rook') 

        elif self.game_state == 'castle the rook':
            assert self.selected_sprite and self.selected_start and self.selected_end
            assert None not in (self.moving_dx, self.moving_dy, self.moving_steps)
            assert self.previous_castle_state in ('queenside castle', 'kingside castle')

            if self.moving_steps > 0:
                # Move the sprite a little
                self.moving_steps -= 1
                self.selected_sprite.x += self.moving_dx
                self.selected_sprite.y += self.moving_dy
            else:
                # Finalize the moving sprite
                self.move_sprite_on_board(self.selected_sprite, *self.selected_end)
                # Update the chess board
                team = chess.get_current_team(self.turn)
                if self.previous_castle_state == 'queenside castle':
                    self.chess_board.move_queenside_castle(team)
                elif self.previous_castle_state == 'kingside castle':
                    self.chess_board.move_kingside_castle(team) 
                self.turn += 1
                self.play_sound('castle')
                self.enter_game_state('wait')

        elif self.game_state == 'checkmate':
            # Wait to play the checkmate sound
            if self.sound_delay is not None:
                if self.sound_delay > 0:
                    self.sound_delay -= 1
                else: 
                    self.sound_delay = None
                    self.play_sound('checkmate')
            # Check for the player to click on their king to resign
            if self.input_is_fresh:
                self.input_is_fresh = False
                if rowcol := screen_to_board(self.input_x, self.input_y):
                    if sprite := self.get_sprite_at(*rowcol):
                        losing_king = chess.get_current_team(self.turn)
                        if sprite.piece == losing_king:
                            self.enter_game_state('resign')

        elif self.game_state == 'resign':
            if self.move_steps > 0:
                self.move_steps -= 1
            else:
                # Reset the game
                self.__init__(self.screen)
        else:
            raise ValueError('invalid Game.game_state')

        self.update_timers()
        self.update_message()

    def create_highlight_sprites (self):
        self.highlight_sprites = [Sprite(330, *board_to_screen(*self.selected_start), 2)]
        moves = self.chess_board.piece_moves(*self.selected_start)
        team = chess.get_current_team(self.turn)
        for move in moves:
            if self.chess_board.is_legal_move(team, *self.selected_start, *move):
                x, y = board_to_screen(*move)
                sprite = Sprite(328, x, y, 2)
                self.highlight_sprites.append(sprite)

    def is_move_queenside_castle (self, start_row, start_col, end_row, end_col):
        # Input pattern for castling queenside
        if chess.get_current_team(self.turn) == chess.BLACK_KING:
            row = 0
        else:
            row = 7
        start_is_king  = start_row == row and start_col == 4
        end_is_castling = end_row == row and end_col == 2
        return start_is_king and end_is_castling

    def is_move_kingside_castle (self, start_row, start_col, end_row, end_col):
        # Input pattern for castling kingside
        if chess.get_current_team(self.turn) == chess.BLACK_KING:
            row = 0
        else:
            row = 7
        start_is_king  = start_row == row and start_col == 4
        end_is_castling = end_row == row and end_col == 6
        return start_is_king and end_is_castling

    def update_result_sounds (self):
        if self.chess_board.get_winner():
            self.play_sound('checkmate')
        elif self.chess_board.king_is_in_check(chess.get_current_team(self.turn)):
            self.play_sound('check')

    def display (self):
        self.display_background()
        if self.state == 'play':
            # Highlighted squares
            for sprite in self.highlight_sprites:
                draw_tile(self.screen, self.spritesheet, sprite.tile, sprite.x, sprite.y, 2)
            # Game piece sprites
            for sprite in self.pieces:
                draw_tile(self.screen, self.spritesheet, sprite.tile, sprite.x, sprite.y, sprite.size)
            # Message character sprites
            for sprite in self.message_sprites:
                draw_tile(self.screen, self.spritesheet, sprite.tile, sprite.x, sprite.y)
            self.display_number(self.black_minutes, 104, 8)
            self.display_number(self.black_seconds, 128, 8)
            self.display_number(self.white_minutes, 104, 224)
            self.display_number(self.white_seconds, 128, 224)
        elif self.state == 'menu':
            cursor = 257
            draw_tile(self.screen, self.spritesheet, cursor, 80, self.cursor_y)
        elif self.state == 'transition':
            tile = 316 + self.num_players 
            draw_tile(self.screen, self.spritesheet, tile, 72, 56)

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
    screen2 = pygame.Surface((WIDTH * SCALE, HEIGHT * SCALE))
    game = Game(screen)
    while game.running:
        for event in pygame.event.get():
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
