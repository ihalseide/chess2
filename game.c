#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <raylib.h>
#define STB_DS_IMPLEMENTATION
#include "stb_ds.h"

typedef enum GameState
{
	GS_OTHER,
	GS_PLAY,
} GameState;

typedef enum NormalChessKind
{
	WHITE_KING,
	WHITE_QUEEN,
	WHITE_ROOK,
	WHITE_BISHOP,
	WHITE_KNIGHT,
	WHITE_PAWN,
	BLACK_KING,
	BLACK_QUEEN,
	BLACK_ROOK,
	BLACK_BISHOP,
	BLACK_KNIGHT,
	BLACK_PAWN,
} NormalChessKind;

typedef struct NormalChessPiece
{
	NormalChessKind kind;
	int row; // position row
	int col; // position column
} NormalChessPiece;

typedef struct NormalChess
{
	int turn;
	NormalChessPiece **arrPieces; // dynamic array
} NormalChess;

Texture2D spritesheet;
GameState theState = GS_PLAY;
int ticks = 0;

NormalChessPiece *NormalChessPieceAlloc(NormalChessKind k, int row, int col)
{
	NormalChessPiece *new = malloc(sizeof(*new));
	assert(new);
	new->kind = k;
	new->row = row;
	new->col = col;
	return new;
}

void NormalChessPieceFree(NormalChessPiece *p)
{
	free(p);
}

// arrPieces is a dynamic array
NormalChess *NormalChessAlloc(int turn, NormalChessPiece **arrPieces)
{
	NormalChess *new = malloc(sizeof(*new));
	assert(new);
	new->turn = turn;
	new->arrPieces = arrPieces;
	return new;
}

void NormalChessFree(NormalChess *p)
{
	free(p);
}

// Allocates new
NormalChess *NormalChessInit(void)
{
	NormalChessPiece **pieces = NULL;
	// Create the pawn ranks
	for (int col = 0; col < 8; col++)
	{
		NormalChessPiece *p;
		p = NormalChessPieceAlloc(WHITE_PAWN, 1, col);
		arrpush(pieces, p);
		p = NormalChessPieceAlloc(BLACK_PAWN, 6, col);
		arrpush(pieces, p);
	}
	return NormalChessAlloc(0, pieces);
}

void NormalChessDestroy(NormalChess *p)
{
	int len = arrlen(p->arrPieces);
	for (int i = 0; i < len; i++)
	{
		NormalChessPieceFree(p->arrPieces[i]);
	}
	arrfree(p->arrPieces);
	NormalChessFree(p);
}

void DrawChessBoard(int x0, int y0, int tileSize, int width, int height)
{
	for (int x = 0; x < width; x++)
	{
		for (int y = 0; y < height; y++)
		{
			Color color;
			if (x % 2 != y %2)
			{
				color = BLACK;
			}
			else
			{
				color = WHITE;
			}
			DrawRectangle(x0 + x * tileSize,
					y0 + y * tileSize,
					tileSize,
					tileSize,
					color);
		}
	}
}

void NormalChessDraw(void)
{
	DrawChessBoard(40, 40, 16, 8, 8);
}

void update(void) {
	ticks++;
}

void drawPlay(void)
{
	// Tick count
	char msg[20];
	snprintf(msg, sizeof(msg), "Ticks: %d", ticks);
	ClearBackground(RAYWHITE);
	NormalChessDraw();
	DrawText(msg, 20, 20, 16, GREEN);

}

void draw(void) {
	switch (theState)
	{
		case GS_PLAY:
			drawPlay();
			break;
		default:
			ClearBackground(RAYWHITE);
			DrawText("Unknown game state", 5, 5, 16, RED);
			break;
	}
}

int main(void) {
    const int screenWidth = 600;
    const int screenHeight = 480;
    InitWindow(screenWidth, screenHeight, "Chezz");
    SetTargetFPS(30);

    spritesheet = LoadTexture("gfx/textures.png");

    while (!WindowShouldClose()) {
        update();
        BeginDrawing();
        draw();
        EndDrawing();
    }

	CloseWindow();

    return 0;
}
