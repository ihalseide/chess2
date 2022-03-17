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

// Normal-chess game data
typedef struct NormalChess
{
	int turn;
	NormalChessPiece **arrPieces; // dynamic array
} NormalChess;

Texture2D theSpritesheet;
GameState theState = GS_PLAY;
int ticks = 0;
NormalChess *theNormalChess = NULL;

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
	NormalChessPiece *p;
	// Create the pawn ranks
	for (int col = 0; col < 8; col++)
	{
		p = NormalChessPieceAlloc(WHITE_PAWN, 1, col);
		arrpush(pieces, p);
		p = NormalChessPieceAlloc(BLACK_PAWN, 6, col);
		arrpush(pieces, p);
	}
	// White pieces
	p = NormalChessPieceAlloc(WHITE_ROOK, 0, 0);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(WHITE_KNIGHT, 0, 1);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(WHITE_BISHOP, 0, 2);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(WHITE_QUEEN, 0, 3);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(WHITE_KING, 0, 4);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(WHITE_BISHOP, 0, 5);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(WHITE_KNIGHT, 0, 6);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(WHITE_ROOK, 0, 7);
	arrpush(pieces, p);
	// Black pieces
	p = NormalChessPieceAlloc(BLACK_ROOK, 7, 0);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(BLACK_KNIGHT, 7, 1);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(BLACK_BISHOP, 7, 2);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(BLACK_QUEEN, 7, 3);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(BLACK_KING, 7, 4);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(BLACK_BISHOP, 7, 5);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(BLACK_KNIGHT, 7, 6);
	arrpush(pieces, p);
	p = NormalChessPieceAlloc(BLACK_ROOK, 7, 7);
	arrpush(pieces, p);
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
	Color c1 = WHITE;
	Color c2 = BLACK;
	for (int x = 0; x < width; x++)
	{
		for (int y = 0; y < height; y++)
		{
			Color color;
			if (x % 2 == y %2)
			{
				color = c1;
			}
			else
			{
				color = c2;
			}
			DrawRectangle(x0 + x * tileSize,
					y0 + y * tileSize,
					tileSize,
					tileSize,
					color);
		}
	}
}

// Rectangle slice of where a piece kind's texture is on
// the spritesheet.
Rectangle NormalChessKindToTextureRect(NormalChessKind k)
{
	assert(WHITE_KING <= k);
	assert(BLACK_PAWN >= k);
	static const Rectangle lookup[] =
	{
		[WHITE_KING]   = (Rectangle){ 80,  64, 16, 16 },
		[WHITE_QUEEN]  = (Rectangle){ 64,  64, 16, 16 },
		[WHITE_ROOK]   = (Rectangle){ 48,  64, 16, 16 },
		[WHITE_BISHOP] = (Rectangle){ 16,  64, 16, 16 },
		[WHITE_KNIGHT] = (Rectangle){ 32,  64, 16, 16 },
		[WHITE_PAWN]   = (Rectangle){ 0,   64, 16, 16 },
		[BLACK_KING]   = (Rectangle){ 174, 64, 16, 16 },
		[BLACK_QUEEN]  = (Rectangle){ 160, 64, 16, 16 },
		[BLACK_ROOK]   = (Rectangle){ 144, 64, 16, 16 },
		[BLACK_BISHOP] = (Rectangle){ 112, 64, 16, 16 },
		[BLACK_KNIGHT] = (Rectangle){ 128, 64, 16, 16 },
		[BLACK_PAWN]   = (Rectangle){ 96,  64, 16, 16 },
	};
	return lookup[k];
}

void NormalChessDraw(NormalChess *game)
{
	int x0 = 40;
	int y0 = 40;
	int sz = 16;
	DrawChessBoard(x0, y0, sz, 8, 8);
	// Draw pieces
	int len = arrlen(game->arrPieces);
	for (int i = 0; i < len; i++)
	{
		NormalChessPiece p = *(game->arrPieces[i]);
		Rectangle slice = NormalChessKindToTextureRect(p.kind);
		int x = p.col * sz + x0;
		int y = (7 - p.row) * sz + y0; // 0th row is at the bottom
		Vector2 pos = (Vector2){ x, y };
		DrawTextureRec(theSpritesheet, slice, pos, WHITE);
	}
}

void Update(void) {
	ticks++;
}

void DrawPlay(void)
{
	// Tick count
	char msg[20];
	snprintf(msg, sizeof(msg), "Ticks: %d", ticks);
	ClearBackground(RAYWHITE);
	NormalChessDraw(theNormalChess);
	DrawText(msg, 20, 20, 16, GREEN);

}

void Draw(void) {
	switch (theState)
	{
		case GS_PLAY:
			DrawPlay();
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

    theSpritesheet = LoadTexture("gfx/textures.png");

	theNormalChess = NormalChessInit();

    while (!WindowShouldClose()) {
        Update();
        BeginDrawing();
        Draw();
        EndDrawing();
    }

	CloseWindow();

    return 0;
}
