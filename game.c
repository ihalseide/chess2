#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "raylib.h"
#define STB_DS_IMPLEMENTATION
#include "stb_ds.h"

#define TILE_SIZE 16
#define HI_COLOR (Color){ 210, 210, 10, 128 }

#define abs(x) (((x) > 0)? (x) : -(x))
#define sign(x) ((x)? (((x) > 0)? 1 : -1) : 0)

// TODO: implement pawn promotion

typedef enum GameState
{
	GS_OTHER,
	GS_PLAY,
	GS_GAME_OVER,
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
	int doublePawnCol; // column of the most recent double pawn move
	int hasWhiteKingMoved;
	int hasWhiteKingsRookMoved;
	int hasWhiteQueensRookMoved;
	int hasBlackKingMoved;
	int hasBlackKingsRookMoved;
	int hasBlackQueensRookMoved;
	NormalChessPiece **arrPieces; // dynamic array
} NormalChess;

typedef struct ViewContext
{
	Texture2D spritesheet;
} ViewContext;

typedef struct GameContext
{
	int ticks;
	GameState state;
	NormalChess *normalChess;
	int tileSize;
	Vector2 boardOffset; // pixels
	Vector2 clickStart; // pixels
	NormalChessPiece *draggedPiece;
	Vector2 *arrDraggedPieceMoves; // board coordinates (col, row)
} GameContext;

const char *NormalChessKindToStr(NormalChessKind k)
{
	switch (k)
	{
		case WHITE_KING:   return "WHITE_KING";
		case WHITE_QUEEN:  return "WHITE_QUEEN";
		case WHITE_ROOK:   return "WHITE_ROOK";
		case WHITE_BISHOP: return "WHITE_BISHOP";
		case WHITE_KNIGHT: return "WHITE_KNIGHT";
		case WHITE_PAWN:   return "WHITE_PAWN";
		case BLACK_KING:   return "BLACK_KING";
		case BLACK_QUEEN:  return "BLACK_QUEEN";
		case BLACK_ROOK:   return "BLACK_ROOK";
		case BLACK_BISHOP: return "BLACK_BISHOP";
		case BLACK_KNIGHT: return "BLACK_KNIGHT";
		case BLACK_PAWN:   return "BLACK_PAWN";
		default:
			return "(invalid)";
	}
}

// Search dynamic array for vector2
int Vector2ArrFind(Vector2 *arrVectors, Vector2 val)
{
	for (int i = 0; i < arrlen(arrVectors); i++)
	{
		Vector2 val2 = arrVectors[i];
		if (val2.x == val.x && val2.y == val.y)
		{
			return i;
		}
	}
	return -1;
}

void ClearMoveSquares(GameContext *game)
{
	if (game->arrDraggedPieceMoves != NULL)
	{
		arrfree(game->arrDraggedPieceMoves);
	}
	game->arrDraggedPieceMoves = NULL;
}

int NormalChessPieceTeamEq(NormalChessPiece *a, NormalChessPiece *b)
{
	return a && b && (a->kind < BLACK_KING) == (b->kind < BLACK_KING);
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
	new->doublePawnCol = -1;
	new->hasWhiteKingMoved = 0;
	new->hasWhiteKingsRookMoved = 0;
	new->hasWhiteQueensRookMoved= 0;
	new->hasBlackKingMoved = 0;
	new->hasBlackKingsRookMoved = 0;
	new->hasBlackQueensRookMoved = 0;
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

void DrawNormalChess(const GameContext *game, ViewContext *vis)
{
	int x0 = game->boardOffset.x;
	int y0 = game->boardOffset.y;
	int tileSize = game->tileSize;
	// Draw board
	DrawChessBoard(x0, y0, tileSize, 8, 8);
	// Draw pieces
	for (int i = 0; i < arrlen(game->normalChess->arrPieces); i++)
	{
		NormalChessPiece p = *(game->normalChess->arrPieces[i]);
		Rectangle slice = NormalChessKindToTextureRect(p.kind);
		int x = 8 + p.col * tileSize + x0;
		int y =  8 + (7 - p.row) * tileSize + y0; // 0th row is at the bottom
		Vector2 pos = (Vector2){ x, y };
		DrawTextureRec(vis->spritesheet, slice, pos, WHITE);
	}
	// Debug info:
	//char msg[100];
	//int x1 = 15, y1 = 5;
	//snprintf(msg, sizeof(msg), "hasWhiteKingMoved:%d", game->normalChess->hasWhiteKingMoved);
	//DrawText(msg, x1, y1, 17, WHITE);
	//snprintf(msg, sizeof(msg), "hasWhiteKingsRookMoved:%d", game->normalChess->hasWhiteKingsRookMoved);
	//DrawText(msg, x1, y1 + 17, 16, WHITE);
	//snprintf(msg, sizeof(msg), "hasWhiteQueensRookMoved:%d", game->normalChess->hasWhiteQueensRookMoved);
	//DrawText(msg, x1, y1 + 17*2, 16, WHITE);
	//snprintf(msg, sizeof(msg), "hasBlackKingMoved:%d", game->normalChess->hasBlackKingMoved);
	//DrawText(msg, x1, y1 + 17*3, 16, WHITE);
	//snprintf(msg, sizeof(msg), "hasBlackKingsRookMoved:%d", game->normalChess->hasBlackKingsRookMoved);
	//DrawText(msg, x1, y1 + 17*4, 16, WHITE);
	//snprintf(msg, sizeof(msg), "hasBlackQueensRookMoved:%d", game->normalChess->hasBlackQueensRookMoved);
	//DrawText(msg, x1, y1 + 17*5, 16, WHITE);
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

// Get the king of a chess piece kind.
NormalChessKind NormalChessKingKind(NormalChessKind k)
{
	switch (k)
	{
		case WHITE_KING:
		case WHITE_QUEEN:
		case WHITE_ROOK:
		case WHITE_BISHOP:
		case WHITE_KNIGHT:
		case WHITE_PAWN:
			return WHITE_KING;
		case BLACK_KING:
		case BLACK_QUEEN:
		case BLACK_ROOK:
		case BLACK_BISHOP:
		case BLACK_KNIGHT:
		case BLACK_PAWN:
			return BLACK_KING;
		default:
			assert(0 && "invalid piece kind");
	}
}

NormalChessKind NormalChessEnemyKingKind(NormalChessKind k)
{
	return (NormalChessKingKind(k) == WHITE_KING)? BLACK_KING : WHITE_KING;
}

NormalChessKind PieceKingOf(NormalChessPiece *p)
{
	assert(p);
	return NormalChessKingKind(p->kind);
}

// Find the king piece for a kind.
NormalChessPiece *PiecesFindKing(NormalChessPiece **arrPieces, NormalChessKind k)
{
	assert(arrPieces);
	NormalChessKind king = NormalChessKingKind(k);
	for (int i = 0; i < arrlen(arrPieces); i++)
	{
		NormalChessPiece *p = arrPieces[i];
		assert(p);
		if (p->kind == king)
		{
			return p;
		}
	}
	return NULL;
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
	NormalChessPiece *p = PiecesGetAt(arrPieces, startRow, startCol);
	if (!p)
		assert(p);
	p->row = targetRow;
	p->col = targetCol;
}

// Remove the piece at target and move the piece at start to the target.
void PiecesDoCapture(NormalChessPiece **arrPieces, int startRow, int startCol,
		int targetRow, int targetCol)
{
	assert(arrPieces);
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

// Pawns and sliding pieces
int PiecesMoveIsBlocked(NormalChessPiece **arrPieces, NormalChessPiece *p, int targetRow, int targetCol)
{
	assert(arrPieces);
	assert(p);
	switch (p->kind)
	{
		case WHITE_PAWN:
		case BLACK_PAWN:
			// Pawn is blocked for diagonal moves if there is no
			// piece for it to capture at the square.
			return targetCol != p->col
					&& !PiecesGetAt(arrPieces, targetRow, targetCol);
		case WHITE_QUEEN:
		case BLACK_QUEEN:
		case WHITE_BISHOP:
		case BLACK_BISHOP:
		case WHITE_ROOK:
		case BLACK_ROOK:
			// Is a sliding piece, so trace the path from the piece to the target.
			// And if any piece is found along the way, the square is blocked.
			{
				int dRow = sign(targetRow - p->row);
				int dCol = sign(targetCol - p->col);
				int row = p->row + dRow;
				int col = p->col + dCol;
				while (!(row == targetRow && col == targetCol)
						&& row >= 0 && row <= 7
						&& col >= 0 && col <= 7
						&& !PiecesGetAt(arrPieces, row, col))
				{
					row += dRow;
					col += dCol;
				}
				return row != targetRow || col != targetCol;
			}
		default:
			// A non-sliding piece -> not blocked
			return 0;
	}
}

int PiecesCanTeamCaptureSpot(NormalChessPiece **arrPieces, NormalChessKind team, int targetRow, int targetCol)
{
	for (int i = 0; i < arrlen(arrPieces); i++)
	{
		NormalChessPiece *member = arrPieces[i];
		assert(member);
		// Note: do not check special moves.
		if (PieceKingOf(member) == NormalChessKingKind(team)
				&& NormalChessMovesContains(member, targetRow, targetCol)
				&& !PiecesMoveIsBlocked(arrPieces, member, targetRow, targetCol))
		{
			return 1;
		}
	}
	return 0;
}


// Special moves in normal chess:
//  - Pawns -> double first move and en passant
//  - Kings -> castling
int NormalChessSpecialMovesContains(const NormalChess *chess,
		const NormalChessPiece *p, int row, int col)
{
	int dRow = row - p->row;
	int dCol = col - p->col;
	NormalChessKind enemyKing = NormalChessEnemyKingKind(p->kind);
	switch (p->kind)
	{
		case WHITE_PAWN:
			// Double first move OR En passant
			if (p->row == 1 && dRow == 2 && dCol == 0)
			{
				// Double first move
				return 1;
			}
			else if (p->row == 4 && dRow == 1 && chess->doublePawnCol == col)
			{
				// En passant
				NormalChessPiece *other = PiecesGetAt(chess->arrPieces, p->row, col);
				return other && other->kind == BLACK_PAWN;
			}
			else
			{
				return 0;
			}
		case BLACK_PAWN:
			// Double first move OR En passant
			if (p->row == 6 && dRow == -2 && dCol == 0)
			{
				// Double first move
				return 1;
			}
			else if (p->row == 3 && dRow == -1 && chess->doublePawnCol == col)
			{
				// En passant
				NormalChessPiece *other = PiecesGetAt(chess->arrPieces, p->row, col);
				return other && other->kind == WHITE_PAWN;
			}
			else
			{
				return 0;
			}
		case WHITE_KING:
			if (PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col))
			{
				// Cannot castle when in the king is in check.
				return 0;
			}
			else if (dCol > 0)
			{
				// King's side castle
				return !chess->hasWhiteKingMoved 
					&& !chess->hasWhiteKingsRookMoved
					&& dCol == 2
					&& dRow == 0
					&& !PiecesGetAt(chess->arrPieces, p->row, p->col + 1)
					&& !PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col + 1)
					&& !PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col + 2);
			}
			else if (dCol < 0)
			{
				// Queen's side castle
				return !chess->hasWhiteKingMoved 
					&& !chess->hasWhiteQueensRookMoved
					&& dCol == -2
					&& dRow == 0
					&& !PiecesGetAt(chess->arrPieces, p->row, p->col - 1)
					&& !PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col - 1)
					&& !PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col - 2)
					&& !PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col - 3);
			}
			else
			{
				return 0;
			}
		case BLACK_KING:
			if (PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col))
			{
				// Cannot castle when in the king is in check.
				return 0;
			}
			if (dCol > 0)
			{
				// King's side castle
				return !chess->hasBlackKingMoved 
					&& !chess->hasBlackKingsRookMoved
					&& dCol == 2
					&& dRow == 0
					&& !PiecesGetAt(chess->arrPieces, p->row, p->col + 1)
					&& !PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col + 1)
					&& !PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col + 2);
			}
			else if (dCol < 0)
			{
				// Queen's side castle
				return !chess->hasBlackKingMoved 
					&& !chess->hasBlackQueensRookMoved
					&& dCol == -2
					&& dRow == 0
					&& !PiecesGetAt(chess->arrPieces, p->row, p->col - 1)
					&& !PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col - 1)
					&& !PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col - 2)
					&& !PiecesCanTeamCaptureSpot(chess->arrPieces, enemyKing, p->row, p->col - 3);
			}
			else
			{
				return 0;
			}
		default:
			return 0;
	}
}

void TestNormalChessMovesContains(void)
{
	// int NormalChessMovesContains(NormalChessPiece p, int row, int col);
	NormalChessPiece p1;

	p1 = (NormalChessPiece){ .kind = WHITE_PAWN, .row = 0, .col = 4 };
	assert(!NormalChessMovesContains(&p1, 0, 4));

	p1 = (NormalChessPiece){ .kind = BLACK_PAWN, .row = 7, .col = 3 };
	assert(!NormalChessMovesContains(&p1, 7, 3));
}

// Move the castle and update castling flags in the chess game.
void NormalChessCastleMove(NormalChess *chess, NormalChessPiece *p, int targetCol)
{
	// Cases: queen's side castle or king's side castle
	assert(chess);
	assert(p);
	assert(targetCol == 6 || targetCol == 2);
	// Move the rook
	int rookStartCol, rookTargetCol;
	if (targetCol > p->col)
	{
		// King's side
		rookStartCol = 7;
		rookTargetCol = 5;
	}
	else if (targetCol < p->col)
	{
		// Queen's side
		rookStartCol = 0;
		rookTargetCol = 3;
	}
	else
	{
		assert(0 && "unreachable");
	}
	// Update castling flags
	switch (p->kind)
	{
		case WHITE_KING:
			chess->hasWhiteKingMoved = 1;
			if (targetCol > p->col)
			{
				chess->hasWhiteKingsRookMoved = 1;
			}
			else
			{
				chess->hasWhiteQueensRookMoved = 1;
			}
			break;
		case BLACK_KING:
			chess->hasBlackKingMoved = 1;
			if (targetCol > p->col)
			{
				chess->hasBlackKingsRookMoved = 1;
			}
			else
			{
				chess->hasBlackQueensRookMoved = 1;
			}
			break;
		default:
			assert(0 && "unreachable");
	}
	PiecesDoMove(chess->arrPieces, p->row, rookStartCol, p->row, rookTargetCol);
}

void NormalChessPawnMove(NormalChess *chess, NormalChessPiece *p, int targetRow, int targetCol)
{
	// Cases: capture move, en passant move, or first move is a double move.
	int dRow = targetRow - p->row;
	int dCol = targetCol - p->col;
	if (abs(dRow) == 2)
	{
		// First move is double move -> update flag
		chess->doublePawnCol = p->col;
	}
	else if (dCol)
	{
		// En passant capture or normal capture.
		// It is en passant if the pawn is moving diagonal to capture and there is no
		// piece to capture at that target square.
		NormalChessPiece *target = PiecesGetAt(chess->arrPieces, targetRow, targetCol);
		if (!target)
		{
			// En passant capture -> remove the other pawn which is next to this one
			NormalChessPiece *other = PiecesGetAt(chess->arrPieces, p->row, targetCol);
			assert(other);
			assert(other->kind == WHITE_PAWN || other->kind == BLACK_PAWN);
			PiecesRemovePieceAt(chess->arrPieces, p->row, targetCol);
		}
	}
	else
	{
		assert(0 && "unreachable");
	}
}

// Update any flags that result from moving the king or rooks (for castling).
void NormalChessUpdateFlagsFromMove(NormalChess *chess, NormalChessPiece *p, int startCol)
{
	assert(chess);
	assert(p);
	switch (p->kind)
	{
		case WHITE_PAWN:
		case BLACK_PAWN:
			// Reset the doublePawnCol flag if it wasn't set from this move.
			if (startCol != chess->doublePawnCol)
			{
				chess->doublePawnCol = -1;
			}
			break;
		case WHITE_KING:
			chess->hasWhiteKingMoved = 1;
			break;
		case BLACK_KING:
			chess->hasBlackKingMoved = 1;
			break;
		case WHITE_ROOK:
			if (startCol == 7)
			{
				chess->hasWhiteKingsRookMoved = 1;
			}
			else if (startCol == 0)
			{
				chess->hasWhiteQueensRookMoved = 1;
			}
			break;
		case BLACK_ROOK:
			if (startCol == 7)
			{
				chess->hasBlackKingsRookMoved = 1;
			}
			else if (startCol == 0)
			{
				chess->hasBlackQueensRookMoved = 1;
			}
			break;
		default:
			break;
	}
}

// Handle normal moves and special moves like castling.
// Also update the turn counter.
void NormalChessDoFullMove(NormalChess *chess, int startRow, int startCol,
		int targetRow, int targetCol)
{
	assert(chess);
	assert(chess->arrPieces);
	NormalChessPiece *p = PiecesGetAt(chess->arrPieces, startRow, startCol);
	// Handle special conditions before the normal move.
	if (NormalChessSpecialMovesContains(chess, p, targetRow, targetCol))
	{
		switch (p->kind)
		{
			case WHITE_KING:
			case BLACK_KING:
				NormalChessCastleMove(chess, p, targetCol);
				break;
			case WHITE_PAWN:
			case BLACK_PAWN:
				NormalChessPawnMove(chess, p, targetRow, targetCol);
				break;
			default:
				assert(0 && "did not handle all special moves");
		}
	}
	// Do the normal piece movement
	PiecesDoCapture(chess->arrPieces, startRow, startCol, targetRow, targetCol);
	// Update any flags that result from moving the king or rooks (for castling).
	NormalChessUpdateFlagsFromMove(chess, p, startCol);
	chess->turn++;
}

// See if a piece is prevented from moving to a target square because it is pinned.
int PiecesIsPiecePinned(NormalChessPiece **arrPieces, NormalChessPiece *p, int targetRow, int targetCol)
{
	assert(p);
	NormalChessPiece *king = PiecesFindKing(arrPieces, p->kind);
	if (!king)
	{
		// No king means that the pieces cannot move.
		return 1;
	}
	int originalRow = p->row;
	int originalCol = p->col;
	// Temporarily move the piece to where it want to go to see "what if".
	p->row = targetRow;
	p->col = targetCol;
	// Check if any of the enemy pieces may capture the king.
	int isPinned = PiecesCanTeamCaptureSpot(arrPieces, NormalChessEnemyKingKind(PieceKingOf(p)), king->row, king->col);
	// Restore the pieces original position.
	p->row = originalRow;
	p->col = originalCol;
	return isPinned;
}

int NormalChessAllMovesContains(NormalChess *c, NormalChessPiece *p, int row, int col)
{
	// Must be a square within the piece's normal moves or special moves.
	int special = NormalChessSpecialMovesContains(c, p, row, col);
	if (!NormalChessMovesContains(p, row, col) && !special)
	{
		return 0;
	}
	// A piece cannot capture any pieces on the same team.
	NormalChessPiece *other = PiecesGetAt(c->arrPieces, row, col);
	if (other && NormalChessPieceTeamEq(p, other))
	{
		return 0;
	}
	// A sliding piece's moves are blocked by the first piece hit.
	if (!special && PiecesMoveIsBlocked(c->arrPieces, p, row, col))
	{
		return 0;
	}
	// A piece may not move if it is pinned to the king
	if (PiecesIsPiecePinned(c->arrPieces, p, row, col))
	{
		return 0;
	}
	// Exception: pawns cannot capture forward.
	if ((p->kind == WHITE_PAWN || p->kind == BLACK_PAWN)
			&& col == p->col
			&& PiecesGetAt(c->arrPieces, row, col))
	{
		return 0;
	}
	return 1;
}

// Get a list of all valid moves for a piece.
// Returns: new dynamic array of (col, row).
Vector2 *NormalChessCreatePieceMoveList(NormalChess *c, NormalChessPiece *p)
{
	Vector2 *result = NULL;
	for (int row = 0; row < 8; row++)
	{
		for (int col = 0; col < 8; col++)
		{
			if (NormalChessAllMovesContains(c, p, row, col))
			{
				Vector2 colRow = (Vector2){ col, row };
				arrpush(result, colRow);
			}
		}
	}
	return result;
}

NormalChessKind NormalChessCurrentKing(NormalChess *chess)
{
	return (chess->turn % 2 == 0)? WHITE_KING : BLACK_KING;
}

int NormalChessIsKingInCheck(NormalChess *chess)
{
	NormalChessKind currentKing = NormalChessCurrentKing(chess);
	NormalChessPiece *king = PiecesFindKing(chess->arrPieces, currentKing);
	if (!king)
	{
		return 0;
	}
	return PiecesCanTeamCaptureSpot(chess->arrPieces, NormalChessEnemyKingKind(currentKing), king->row, king->col);
}

int NormalChessCanMove(NormalChess *chess)
{
	assert(chess);
	NormalChessKind king = NormalChessCurrentKing(chess);
	// Check if any pieces on the curren team can move.
	for (int i = 0; i < arrlen(chess->arrPieces); i++)
	{
		NormalChessPiece *p = chess->arrPieces[i];
		assert(p);
		if (PieceKingOf(p) == king)
		{
			Vector2 *moves = NormalChessCreatePieceMoveList(chess, p);
			if (moves != NULL)
			{
				arrfree(moves);
				return 1;
			}
			else
			{
				arrfree(moves);
			}
		}
	}
	return 0;
}

int NormalChessIsStalemate(NormalChess *chess)
{
	return !NormalChessIsKingInCheck(chess) && !NormalChessCanMove(chess);
}

int NormalChessIsCheckmate(NormalChess *chess)
{
	return NormalChessIsKingInCheck(chess) && !NormalChessCanMove(chess);
}

int NormalChessIsGameOver(NormalChess *chess)
{
	return !NormalChessCanMove(chess)
		|| !PiecesFindKing(chess->arrPieces, WHITE_KING)
		|| !PiecesFindKing(chess->arrPieces, BLACK_KING);
}

void UpdateMoveSquares(GameContext *game, NormalChessPiece *p)
{
	assert(game);
	assert(p);
	if (game->arrDraggedPieceMoves)
	{
		ClearMoveSquares(game);
	}
	game->arrDraggedPieceMoves = NormalChessCreatePieceMoveList(game->normalChess, p);
}

void UpdatePlay(GameContext *game)
{
	int x0 = game->boardOffset.x;
	int y0 = game->boardOffset.y;
	int tileSize = game->tileSize;
	Rectangle boardRect = (Rectangle){ x0, y0, 8 * tileSize, 8 * tileSize };

	//if (NormalChessIsGameOver(game->normalChess))
	//{
	//	game->state = GS_GAME_OVER;
	//	return;
	//}

	if (IsMouseButtonPressed(0))
	{
		game->clickStart = GetMousePosition();
		// If clicking on a piece, update the selected piece's available moves.
		if (CheckCollisionPointRec(game->clickStart, boardRect))
		{
			int startRow, startCol;
			ScreenToNormalChessPos(game->clickStart.x, game->clickStart.y, x0, y0, tileSize, &startRow, &startCol); 
			NormalChessPiece *p = PiecesGetAt(game->normalChess->arrPieces, startRow, startCol);
			NormalChessKind currentTurnKing = NormalChessCurrentKing(game->normalChess);
			if (p && PieceKingOf(p) == currentTurnKing)
			{
				game->draggedPiece = p;
				ClearMoveSquares(game);
				if (p)
				{
					UpdateMoveSquares(game, p);
				}
			}
			else
			{
				game->draggedPiece = NULL;
			}
		}
	}
	else if (IsMouseButtonReleased(0))
	{
		Vector2 clickEnd = GetMousePosition();
		game->draggedPiece = NULL;
		if (CheckCollisionPointRec(game->clickStart, boardRect)
				&& CheckCollisionPointRec(clickEnd, boardRect))
		{
			int startRow, startCol, targetRow, targetCol;
			ScreenToNormalChessPos(game->clickStart.x, game->clickStart.y, x0, y0,
					tileSize, &startRow, &startCol); 
			ScreenToNormalChessPos(clickEnd.x, clickEnd.y, x0, y0,
					tileSize, &targetRow, &targetCol); 
			NormalChessPiece *p = PiecesGetAt(game->normalChess->arrPieces,
					startRow, startCol);
			Vector2 targetPos = (Vector2){ targetCol, targetRow };
			if (startRow == targetRow && startCol == targetCol)
			{
				// A piece was clicked on
			}
			else if (p && 0 <= Vector2ArrFind(game->arrDraggedPieceMoves, targetPos))
			{
				// A piece was dragged
				NormalChessDoFullMove(game->normalChess, startRow, startCol,
						targetRow, targetCol);
				ClearMoveSquares(game);
			}
		}
	}
}

void Update(GameContext *game) {
	switch (game->state)
	{
		case GS_PLAY:
			UpdatePlay(game);
			break;
		case GS_GAME_OVER:
			break;
		default:
			break;
	}
	game->ticks++;
}

void DrawPlay(const GameContext *game, ViewContext *vis)
{
	int x0 = game->boardOffset.x;
	int y0 = game->boardOffset.y;
	int tileSize = game->tileSize;
	ClearBackground(BLUE);
	DrawNormalChess(game, vis);
	// Draw highlighted squares
	for (int i = 0; i < arrlen(game->arrDraggedPieceMoves); i++)
	{
		Vector2 pos = game->arrDraggedPieceMoves[i];
		int x, y;
		TileToScreen(pos.x, 7 - pos.y, x0, y0, tileSize, &x, &y);
		DrawRectangle(x, y, tileSize, tileSize, HI_COLOR);
	}
	// Draw floating dragged piece
	Vector2 newMousePos = GetMousePosition();
	if (game->draggedPiece
			&& (abs(newMousePos.x - game->clickStart.x) > 1
				|| abs(newMousePos.y - game->clickStart.y) > 1))
	{
		Rectangle slice = NormalChessKindToTextureRect(game->draggedPiece->kind);
		Vector2 pos = GetMousePosition();
		pos.x += 10; // offset from mouse cursor
		pos.y += 3;
		DrawTextureRec(vis->spritesheet, slice, pos, WHITE);
	}
	// Check Message
	if (NormalChessIsKingInCheck(game->normalChess))
	{
		DrawText("Check", 100, 20, 24, RED);
	}
	// Debug info: draw list of game pieces
	//if (game->normalChess)
	//{
	//	char msg[50];
	//	int scroll = -2 * (game->ticks % 100);
	//	for (int i = 0; i < arrlen(game->normalChess->arrPieces); i++)
	//	{
	//		NormalChessPiece *p = game->normalChess->arrPieces[i];
	//		snprintf(msg, sizeof(msg), "#%2d: %s at row:%2d, col:%2d",
	//				i, NormalChessKindToStr(p->kind), p->row, p->col);
	//		DrawText(msg, 180, 30 + scroll + i * 16, 20, WHITE);
	//	}
	//}
}

void Draw(const GameContext *game, ViewContext *vis) {
	switch (game->state)
	{
		case GS_PLAY:
			DrawPlay(game, vis);
			break;
		case GS_GAME_OVER:
			DrawText("Game over", 20, 50, 16, RED);
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
	// Init:
    const int screenWidth = 600;
    const int screenHeight = 480;
    InitWindow(screenWidth, screenHeight, "Chess 2");
    SetTargetFPS(30);
	GameContext game = (GameContext)
	{
		.state = GS_PLAY,
		.ticks = 0,
		.clickStart = (Vector2) { -1, -1 },
		.normalChess = NormalChessInit(),
		.boardOffset = (Vector2) { 50, 100 },
		.tileSize = TILE_SIZE * 2,
		.arrDraggedPieceMoves = NULL,
		.draggedPiece = NULL,
	};
	ViewContext vis = (ViewContext)
	{
		.spritesheet = LoadTexture("gfx/textures.png"),
	};
	assert(!NormalChessIsGameOver(game.normalChess));
	// Main loop:
    while (!WindowShouldClose()) {
        Update(&game);
        BeginDrawing();
        Draw(&game, &vis);
        EndDrawing();
    }
	// Clean up files
	UnloadTexture(vis.spritesheet);
	// Clean up the game
	game.draggedPiece = NULL;
	if (game.normalChess)
	{
		NormalChessDestroy(game.normalChess);
		game.normalChess = NULL;
	}
	if (game.arrDraggedPieceMoves)
	{
		arrfree(game.arrDraggedPieceMoves);
		game.arrDraggedPieceMoves = NULL;
	}
	CloseWindow();
    return 0;
}
