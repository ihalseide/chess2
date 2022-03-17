CC=gcc
CFLAGS=-Wall -g -std=c99 -I /usr/local/include/ -I.
LFLAGS=-L/raylib/src -L/opt/vc/lii
LIBS=-lraylib 

default: game

game: game.c
	$(CC) $(CFLAGS) $(LFLAGS) game.c -o game $(LIBS)

#%.o: %.c %.h
#	$(CC) $(CFLAGS) $(LFLAGS) .....
