CC=gcc
CFLAGS=-g -std=c99
LFLAGS=
LIBS=-lraylib -lm -ldl -lpthread

default: game

game: main.c game.o tilemap.o
	$(CC) $(CFLAGS) $^ -o $@ -L. $(LIBS)

%.o: %.c %.h
	$(CC) $(CFLAGS) $(LFLAGS) -c $^ -L. $(LIBS)
