CC=gcc
CFLAGS=-Wall -Wextra -std=c99 -I /usr/local/include/ -I.
LFLAGS=-L/raylib/src -L/opt/vc/lii
LIBS=-lraylib 

build: game

run: build
	./game

game: game.c
	$(CC) $(CFLAGS) $(LFLAGS) game.c -o game $(LIBS)

