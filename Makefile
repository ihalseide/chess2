CC=gcc
CFLAGS=-Wall -g -std=c99
LFLAGS=
LIBS=-lraylib -lm -ldl -lpthread

default: game

game: game.c
	$(CC) $(CFLAGS) $^ -o $@ -L. $(LIBS)

%.o: %.c %.h
	$(CC) $(CFLAGS) $(LFLAGS) -c $^ -L. $(LIBS)
