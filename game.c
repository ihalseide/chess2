#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <raylib.h>
#define STB_DS_IMPLEMENTATION
#include "stb_ds.h"

#define TILE_SIZE 16
#define HI_COLOR (Color){ 210, 210, 10, 128 }

#define abs(x) ((x > 0)? x : -x)

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
Vector2 theBoardOffset = (Vector2){ 30, 30 };
//int theZoomScale = 2;
Vector2 theClickStart;
Vector2 *theHiSquares = NULL;

void ClearTheHiSquares(void)
{
	arrfree(theHiSquares);
	theHiSquares = NULL;
}

// Convert screen coordinates to Tile coordinates
void ScreenToTile(int pX, int pY, int x0, int y0, int tileSize, int *tX, int *tY)
{
	*tX = (pX - x0) / tileSize;
	*tY = (pY - y0) / tileSize;
}

// Convert Tile coordinates to Screen coordinates
void TileToScreen(int tX, int tY, int x0, int y0, int tileSize, int *pX, int *pY)
{
	*pX = x0 + tX * tileSize;
	*pY = y0 + tY * tileSize;
}

// Snap screen coordinates to Tile grid
void ScreenSnapCoords(int pX, int pY, int x0, int y0, int tileSize, int *pX2, int *pY2)
{
	int tX, tY;
	ScreenToTile(pX, pY, x0, y0, tileSize, &tX, &tY);
	TileToScreen(tX, tY, x0, y0, tileSize, pX2, pY2);
}

// Convert screen coordinate to row and column for normal chess
void ScreenToNormalChessPos(int pX, int pY, int x0, int y0, int tileSize,
		int *row, int *col)
{
	int tx, ty;
	ScreenToTile(pX, pY, x0, y0, tileSize, &tx, &ty); 
	ty = 7 - ty;
	assert(tx >= 0);
	assert(tx <= 7);
	assert(ty >= 0);
	assert(ty <= 7);
	*row = ty;
	*col = tx;
}

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
	Color c1 = RAYWHITE;
	Color c2 = (Color){ 40, 20, 40, 255 };
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

// Note: argument arrHiSquares = dynamic array of hilighted square positions.
void NormalChessDraw(NormalChess *game, Vector2 *arrHiSquares)
{
	int x0 = theBoardOffset.x;
	int y0 = theBoardOffset.y;
	DrawChessBoard(x0, y0, TILE_SIZE, 8, 8);
	// Draw highlighted squares
	for (int i = 0; i < arrlen(arrHiSquares); i++)
	{
		Vector2 pos = arrHiSquares[i];
		int x, y;
		TileToScreen(pos.x, 7 - pos.y, x0, y0, TILE_SIZE, &x, &y);
		DrawRectangle(x, y, TILE_SIZE, TILE_SIZE, HI_COLOR);
	}
	// Draw pieces
	for (int i = 0; i < arrlen(game->arrPieces); i++)
	{
		NormalChessPiece p = *(game->arrPieces[i]);
		Rectangle slice = NormalChessKindToTextureRect(p.kind);
		int x = p.col * TILE_SIZE + x0;
		int y = (7 - p.row) * TILE_SIZE + y0; // 0th row is at the bottom
		Vector2 pos = (Vector2){ x, y };
		DrawTextureRec(theSpritesheet, slice, pos, WHITE);
	}
}

// Removes any pieces with the given row and column.
// FREEs the piece pointer too!
void PiecesRemovePieceAt(NormalChessPiece **arrPieces, int row, int col)
{
	for (int i = 0; i < arrlen(arrPieces); i++)
	{
		NormalChessPiece *p = arrPieces[i];
		if (p->row == row && p->col == col)
		{
			NormalChessPieceFree(p);
			arrPieces[i] = NULL;
			arrdelswap(arrPieces, i);
		}
	}
}

// Get the first piece found in the array with the given location.
// Returns NULL if no piece is found.
NormalChessPiece *PiecesGetAt(NormalChessPiece **arrPieces, int row, int col)
{
	for (int i = 0; i < arrlen(arrPieces); i++)
	{
		NormalChessPiece *p = arrPieces[i];
		if (p->row == row && p->col == col)
		{
			return p;
		}
	}
	return NULL;
}

// Move the piece at start to target
// (there should not be a piece already at target).
void PiecesDoMove(NormalChessPiece **arrPieces, int startRow, int startCol,
		int targetRow, int targetCol)
{
	assert(!PiecesGetAt(arrPieces, targetRow, targetCol));
	// Find the piece in the array at the location and move it
	for (int i = 0; i < arrlen(arrPieces); i++)
	{
		NormalChessPiece *p = arrPieces[i];
		if (p->row == startRow && p->col == startCol)
		{
			p->row = targetRow;
			p->col = targetCol;
			break;
		}
	}
}

// Remove the piece at target and move the piece at start to the target.
void PiecesDoCapture(NormalChessPiece **arrPieces, int startRow, int startCol,
		int targetRow, int targetCol)
{
	PiecesRemovePieceAt(arrPieces, targetRow, targetCol);
	PiecesDoMove(arrPieces, startRow, startCol, targetRow, targetCol);
}

// Returns if a piece could possibly move to the given location.
int NormalChessMovesContains(const NormalChessPiece *p, int row, int col)
{
	int dRow = row - p->row;
	int dCol = col - p->col;
	// Pieces cannot move to their own square
	if (dRow == 0 && dCol == 0)
	{
		return 0;
	}
	switch (p->kind)
	{
		case WHITE_KING:
		case BLACK_KING:
			// # # #
			// # * #
			// # # #
			return (abs(dRow) <= 1) && (abs(dCol) <= 1);
		case WHITE_QUEEN:
		case BLACK_QUEEN:
			// # . . # . . #
			// . # . # . # .
			// . . # # # . .
			// # # # * # # #
			// . . # # # . .
			// . # . # . # .
			// # . . # . . #
			// Rook || Bishop
			return (dRow == 0 || dCol == 0)
				|| (abs(dRow) == abs(dCol));
		case WHITE_ROOK:
		case BLACK_ROOK:
			// . . . # . . .
			// . . . # . . .
			// . . . # . . .
			// # # # * # # #
			// . . . # . . .
			// . . . # . . .
			// . . . # . . .
			return dRow == 0 || dCol == 0;
		case WHITE_BISHOP:
		case BLACK_BISHOP:
			// # . . . . . #
			// . # . . . # .
			// . . # . # . .
			// . . . * . . .
			// . . # . # . .
			// . # . . . # .
			// # . . . . . #
			return abs(dRow) == abs(dCol);
		case WHITE_KNIGHT:
		case BLACK_KNIGHT:
			// . . # . # . .
			// . # . . . # .
			// . . . * . . .
			// . # . . . # .
			// . . # . # . .
			return (abs(dRow) == 2 && abs(dCol) == 1)
				|| (abs(dRow) == 1 && abs(dCol) == 2);
		case WHITE_PAWN:
			// # # #
			// . * .
			// . . .
			return dRow == 1 && abs(dCol) <= 1;
		case BLACK_PAWN:
			// . . .
			// . * .
			// # # #
			return dRow == -1 && abs(dCol) <= 1;
		default:
			assert(0 && "invalid chess piece kind");
	}
}

void TestNormalChessMovesContains(void)
{
	// int NormalChessMovesContains(NormalChessPiece p, int row, int col);
	NormalChessPiece p1;

	p1 = (NormalChessPiece){ .kind = WHITE_PAWN, .row = 0, .col = 4 };
	assert(!NormalChessMovesContains(&p1, 0, 4));
	assert(!NormalChessMovesContains(&p1, -1, 4));
	assert(!NormalChessMovesContains(&p1, 0, 3));
	assert(!NormalChessMovesContains(&p1, 0, 5));
	assert(!NormalChessMovesContains(&p1, 2, 4)); // no double move
	assert(NormalChessMovesContains(&p1, 1, 4));
	assert(NormalChessMovesContains(&p1, 1, 3));
	assert(NormalChessMovesContains(&p1, 1, 5));

	p1 = (NormalChessPiece){ .kind = BLACK_PAWN, .row = 7, .col = 3 };
	assert(!NormalChessMovesContains(&p1, 7, 3));
	assert(!NormalChessMovesContains(&p1, 8, 3));
	assert(!NormalChessMovesContains(&p1, 7, 2));
	assert(!NormalChessMovesContains(&p1, 7, 4));
	assert(!NormalChessMovesContains(&p1, 5, 3)); // no double move
	assert(NormalChessMovesContains(&p1, 6, 2));
	assert(NormalChessMovesContains(&p1, 6, 3));
	assert(NormalChessMovesContains(&p1, 6, 4));
}

void UpdatePlay(void)
{
	int x0 = theBoardOffset.x;
	int y0 = theBoardOffset.y;
	Rectangle boardRect = (Rectangle){ x0, y0, 8 * TILE_SIZE, 8 * TILE_SIZE };

	if (IsMouseButtonPressed(0))
	{
		theClickStart = GetMousePosition();
		// Update the selected piece's available moves.
		if (CheckCollisionPointRec(theClickStart, boardRect))
		{
			ClearTheHiSquares();

			int startRow, startCol;
			ScreenToNormalChessPos(theClickStart.x, theClickStart.y, x0, y0,
					TILE_SIZE, &startRow, &startCol); 
			NormalChessPiece *p = PiecesGetAt(theNormalChess->arrPieces,
					startRow, startCol);
			if (p)
			{
				for (int row = 0; row < 8; row++)
				{
					for (int col = 0; col < 8; col++)
					{
						if (NormalChessMovesContains(p, row, col))
						{
							Vector2 p = (Vector2) { col, row };
							arrpush(theHiSquares, p);
						}
					}
				}
			}
		}
	}
	else if (IsMouseButtonReleased(0))
	{
		Vector2 clickEnd = GetMousePosition();
		if (CheckCollisionPointRec(theClickStart, boardRect)
				&& CheckCollisionPointRec(clickEnd, boardRect))
		{
			int startRow, startCol, targetRow, targetCol;
			ScreenToNormalChessPos(theClickStart.x, theClickStart.y, x0, y0,
					TILE_SIZE, &startRow, &startCol); 
			ScreenToNormalChessPos(clickEnd.x, clickEnd.y, x0, y0,
					TILE_SIZE, &targetRow, &targetCol); 
			NormalChessPiece *p = PiecesGetAt(theNormalChess->arrPieces,
					startRow, startCol);
			if (startRow == targetRow && startCol == targetCol)
			{
				// A piece was clicked on
			}
			else if (p && NormalChessMovesContains(p, targetRow, targetCol))
			{
				// A piece was dragged
				PiecesDoCapture(theNormalChess->arrPieces, startRow, startCol,
						targetRow, targetCol);
				ClearTheHiSquares();
			}
		}
	}
}

void Update(void) {
	switch (theState)
	{
		case GS_PLAY:
			UpdatePlay();
			break;
		default:
			break;
	}
	ticks++;
}

void DrawPlay(void)
{
	ClearBackground(RAYWHITE);
	NormalChessDraw(theNormalChess, theHiSquares);
}

void Draw(void) {
	switch (theState)
	{
		case GS_PLAY:
			DrawPlay();
			break;
		default:
			ClearBackground(RAYWHITE);
			DrawText("Unknown game state", 20, 50, 16, RED);
			break;
	}
	// Tick count
	//char msg[20];
	//snprintf(msg, sizeof(msg), "Ticks: %d", ticks);
	//DrawText(msg, 10, 10, 16, GREEN);
}

void Test(void)
{
	TestNormalChessMovesContains();
}

int main(void) {
	Test();

    const int screenWidth = 600;
    const int screenHeight = 480;
    InitWindow(screenWidth, screenHeight, "Chess 2");
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
