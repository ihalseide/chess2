#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include "raylib.h"
#define STB_DS_IMPLEMENTATION
#include "stb_ds.h"

#define TEXTURE_TILE_SIZE 16
#define HI_COLOR (Color){ GOLD.r, GOLD.g, GOLD.b, 128 }
#define SELECT_COLOR (Color){ GREEN.r, GREEN.g, GREEN.b, 128 }

#define abs(x) (((x) > 0)? (x) : -(x))
#define sign(x) ((x)? (((x) > 0)? 1 : -1) : 0)

// TODO: fix sprite's reference to a piece getting invalidated after a move.
// TODO: fix not allowing pinned piece to capture (see TODO below later in file).
// TODO: implement pawn promotion.
// TODO: add game turn timers.
// TODO: add gameplay buttons to quit, resign, restart, etc..
// TODO: add particles.
// TODO: add music.

typedef enum GameState
{
	GS_NONE,
	GS_PLAY,
	GS_PLAY_ANIMATE,
	GS_PLAY_PROMOTE,
	GS_GAME_OVER,
	GS_MAIN_MENU,
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

typedef enum SpriteKind
{
	SK_NONE,
	SK_NORMAL_CHESS_PIECE,
} SpriteKind;

typedef struct NormalChessPiece
{
	NormalChessKind kind;
	int row; // position row
	int col; // position column
} NormalChessPiece;

typedef struct NormalChessMove 
{
	int subjectCol;
	int subjectRow;
	int objectCol;
	int objectRow;
	int targetCol;
	int targetRow;
} NormalChessMove;

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

// Tagged union for the data of different kinds of sprites.
typedef struct SpriteData
{
	SpriteKind kind;
	union {
		NormalChessPiece *as_normalChessPiece;
	};
} SpriteData;

typedef struct Sprite
{
	SpriteData data;
	Rectangle boundingBox;
	Rectangle textureRect;
	const Texture2D *refTexture;
} Sprite;

// Note: the .state member should not be modified directly to switch states
// because there may be things to do to clean up the current state. Use the
// function GameSwitchState(...) to switch states.
typedef struct GameContext
{
	int isDebug;  // higher number generally means more info
	int ticks;
	int tileSize;
	Vector2 boardOffset;  // pixels
	GameState state;  // see note above (9 lines above this one)
	Texture2D texPieces;  // spritesheet textures for pieces
	Texture2D texBoard;  // spritesheet textures for board and background
	Texture2D texGUI;  // spritesheet textures for user interface specific stuff
	NormalChess *normalChess;
	Vector2 *arrDraggedPieceMoves;  // board coordinates (col, row)
	Sprite *arrSprites; // dynamic array of sprites
	Sprite *refSelectedSprite;
} GameContext;

// Clamp value to a value between min and max, inclusive of min and max.
void IntClamp(int *value, int min, int max)
{
	if (*value < min)
	{
		*value = min;
	}
	if (*value > max)
	{
		*value = max;
	}
}

float Vector2DistanceSquared(Vector2 a, Vector2 b)
{
	float dx = a.x - b.x;
	float dy = a.y - b.y;
	return dx * dx + dy * dy;
}

const char *GameStateToStr(GameState s)
{
	switch (s)
	{
		case GS_NONE:         return "GS_NONE";
		case GS_PLAY:         return "GS_PLAY";
		case GS_PLAY_PROMOTE: return "GS_PLAY_PROMOTE";
		case GS_GAME_OVER:    return "GS_GAME_OVER";
		case GS_MAIN_MENU:    return "GS_MAIN_MENU";
		default:
			return "(invalid GameState)";
	}
}

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
			return "(invalid NormalChessKind)";
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

NormalChessKind PieceKingOf(const NormalChessPiece *p)
{
	assert(p);
	return NormalChessKingKind(p->kind);
}

// Search dynamic array for vector2
Vector2 *Vector2ArrFind(Vector2 *arrVectors, Vector2 val)
{
	for (int i = 0; i < arrlen(arrVectors); i++)
	{
		Vector2 *val2 = &arrVectors[i];
		if (val2->x == val.x && val2->y == val.y)
		{
			return val2;
		}
	}
	return NULL;
}

// Remove the Sprite from the reference to arrSprites.
// Reallocates the arrSprites, which is why we need a reference to it.
void SpritesArrRemoveSprite(Sprite **refArrSprites, Sprite *removeMe)
{
	Sprite *arrSprites = *refArrSprites;
	for (int i = 0; i < arrlen(arrSprites); i++)
	{
		Sprite *s = &arrSprites[i];
		if (removeMe == s)
		{
			arrdelswap(arrSprites, i);
		}
	}
	*refArrSprites = arrSprites;
}

// Find any sprite at screen coords (x, y)
Sprite *SpritesArrFindSpriteAt(Sprite *arrSprites, int x, int y)
{
	Vector2 p = (Vector2){ x, y };
	for (int i = 0; i < arrlen(arrSprites); i++)
	{
		Sprite *s = &arrSprites[i];
		if (CheckCollisionPointRec(p, s->boundingBox))
		{
			return s;
		}
	}
	return NULL;
}

Sprite *SpritesArrFindNormalChessSpriteAt(Sprite *arrSprites, int col, int row)
{
	for (int i = 0; i < arrlen(arrSprites); i++)
	{
		Sprite *s = &arrSprites[i];
		if (s->data.kind == SK_NORMAL_CHESS_PIECE)
		{
			NormalChessPiece *p = s->data.as_normalChessPiece;
			assert(p);
			if (p->col == col && p->row == row)
			{
				return s;
			}
		}
	}
	return NULL;
}

// Return the sprite that references the given NormalChessPiece.
Sprite *SpritesArrFindNormalChessSpriteFor(Sprite *arrSprites, NormalChessPiece *forPiece)
{
	for (int i = 0; i < arrlen(arrSprites); i++)
	{
		Sprite *s = &arrSprites[i];
		if (s->data.kind == SK_NORMAL_CHESS_PIECE)
		{
			NormalChessPiece *p = s->data.as_normalChessPiece;
			assert(p);
			if (p == forPiece)
			{
				return s;
			}
		}
	}
	return NULL;
}

// Move a sprite so that it is centered at the given position.
void SpriteMoveCenter(Sprite *s, int centerX, int centerY)
{
	int x = centerX - (s->boundingBox.width / 2);
	int y = centerY - (s->boundingBox.height / 2);
	s->boundingBox.x = x;
	s->boundingBox.y = y;
}

void ClearMoveSquares(GameContext *game)
{
	if (game->arrDraggedPieceMoves != NULL)
	{
		arrfree(game->arrDraggedPieceMoves);
	}
	game->arrDraggedPieceMoves = NULL;
}

int NormalChessTeamEq(NormalChessKind a, NormalChessKind b)
{
	return NormalChessKingKind(a) == NormalChessKingKind(b);
}

int NormalChessPieceTeamEq(const NormalChessPiece *a, const NormalChessPiece *b)
{
	return a && b && NormalChessTeamEq(a->kind, b->kind);
}

NormalChessKind NormalChessCurrentKing(const NormalChess *chess)
{
	return (chess->turn % 2 == 0)? WHITE_KING : BLACK_KING;
}

int NormalChessCanUsePiece(const NormalChess *chess, const NormalChessPiece *p)
{
	return chess && p && NormalChessTeamEq(p->kind, NormalChessCurrentKing(chess));
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
void ScreenToNormalChessPos(int pX, int pY, int x0, int y0, int tileSize, int *row, int *col)
{
	int tx, ty;
	ScreenToTile(pX, pY, x0, y0, tileSize, &tx, &ty); 
	// Flip row direction.
	ty = 7 - ty;
	IntClamp(&tx, 0, 7);
	IntClamp(&ty, 0, 7);
	assert(tx >= 0 && tx <= 7);
	assert(ty >= 0 && ty <= 7);
	*col = tx;
	*row = ty;
}

// Inverse of ScreenToNormalChessPos
void NormalChessPosToScreen(int row, int col, int x0, int y0, int tileSize, int *x, int *y)
{
	// Flip row direction.
	row = 7 - row;
	assert(row >= 0 && row <= 7);
	assert(col >= 0 && col <= 7);
	TileToScreen(col, row, x0, y0, tileSize, x, y);
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

void SpriteSetAsNormalChessPiece(Sprite *s, NormalChessPiece *p)
{
	assert(s);
	s->data.kind = SK_NORMAL_CHESS_PIECE;
	s->data.as_normalChessPiece = p;
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
	Color light = BEIGE;
	Color dark = BROWN;
	for (int x = 0; x < width; x++)
	{
		for (int y = 0; y < height; y++)
		{
			Color color;
			if (x % 2 == y %2)
			{
				color = light;
			}
			else
			{
				color = dark;
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

// Find the king piece for a kind.
const NormalChessPiece *PiecesFindKing(const NormalChessPiece **arrPieces, NormalChessKind k)
{
	assert(arrPieces);
	NormalChessKind king = NormalChessKingKind(k);
	for (int i = 0; i < arrlen(arrPieces); i++)
	{
		const NormalChessPiece *p = arrPieces[i];
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

const NormalChessPiece *PiecesGetAtConst(const NormalChessPiece **arrPieces, int row, int col)
{
	for (int i = 0; i < arrlen(arrPieces); i++)
	{
		const NormalChessPiece *p = arrPieces[i];
		if (p->row == row && p->col == col)
		{
			return p;
		}
	}
	return NULL;
}

NormalChessPiece *NormalChessMoveGetSubject(NormalChessMove move, NormalChessPiece **arrPieces)
{
	if (move.subjectRow < 0 || move.subjectRow > 7 || move.subjectCol < 0 || move.subjectCol > 7)
	{
		return NULL;
	}
	return PiecesGetAt(arrPieces, move.subjectRow, move.subjectCol);
}

NormalChessPiece *NormalChessMoveGetObject(NormalChessMove move, NormalChessPiece **arrPieces)
{
	if (move.objectRow < 0 || move.objectRow > 7 || move.objectCol < 0 || move.objectCol > 7)
	{
		return NULL;
	}
	return PiecesGetAt(arrPieces, move.objectRow, move.objectCol);
}

// Move the piece at start to target
// (there should not be a piece already at target).
void PiecesDoMove(NormalChessPiece **arrPieces, int startRow, int startCol,
		int targetRow, int targetCol)
{
	// There should not be a piece at the target location.
	assert(!PiecesGetAt(arrPieces, targetRow, targetCol));
	// Find the piece in the array at the location and move it
	NormalChessPiece *p = PiecesGetAt(arrPieces, startRow, startCol);
	if (p)
	{
		p->row = targetRow;
		p->col = targetCol;
	}
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
int PiecesMoveIsBlocked(const NormalChessPiece **arrPieces, const NormalChessPiece *p, int targetRow,
		int targetCol)
{
	assert(arrPieces);
	assert(p);
	switch (p->kind)
	{
		case WHITE_PAWN:
		case BLACK_PAWN:
			// Pawn is blocked for diagonal moves if there is no
			// piece for it to capture at the square.
			return targetCol != p->col && !PiecesGetAtConst(arrPieces, targetRow, targetCol);
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
						&& !PiecesGetAtConst(arrPieces, row, col))
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

int PiecesCanTeamCaptureSpot(const NormalChessPiece **arrPieces, NormalChessKind team, int targetRow,
		int targetCol)
{
	for (int i = 0; i < arrlen(arrPieces); i++)
	{
		const NormalChessPiece *member = arrPieces[i];
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
int NormalChessSpecialMovesContains(const NormalChess *chess, const NormalChessPiece *p, int row, int col)
{
	if (!p)
	{
		return 0;
	}
	int dRow = row - p->row;
	int dCol = col - p->col;
	NormalChessKind enemyKing = NormalChessEnemyKingKind(p->kind);
	const NormalChessPiece **arrPiecesConst = (const NormalChessPiece **) chess->arrPieces;
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
				const NormalChessPiece *other = PiecesGetAtConst(arrPiecesConst, p->row, col);
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
			{
				if (PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col))
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
						&& !PiecesGetAtConst(arrPiecesConst, p->row, p->col + 1)
						&& !PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col + 1)
						&& !PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col + 2);
				}
				else if (dCol < 0)
				{
					// Queen's side castle
					return !chess->hasWhiteKingMoved 
						&& !chess->hasWhiteQueensRookMoved
						&& dCol == -2
						&& dRow == 0
						&& !PiecesGetAt(chess->arrPieces, p->row, p->col - 1)
						&& !PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col - 1)
						&& !PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col - 2)
						&& !PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col - 3);
				}
				else
				{
					return 0;
				}
				break;
			}
		case BLACK_KING:
			if (PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col))
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
					&& !PiecesGetAtConst(arrPiecesConst, p->row, p->col + 1)
					&& !PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col + 1)
					&& !PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col + 2);
			}
			else if (dCol < 0)
			{
				// Queen's side castle
				return !chess->hasBlackKingMoved 
					&& !chess->hasBlackQueensRookMoved
					&& dCol == -2
					&& dRow == 0
					&& !PiecesGetAtConst(arrPiecesConst, p->row, p->col - 1)
					&& !PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col - 1)
					&& !PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col - 2)
					&& !PiecesCanTeamCaptureSpot(arrPiecesConst, enemyKing, p->row, p->col - 3);
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

NormalChessMove NormalChessCreateCastleMove(NormalChess *chess, NormalChessPiece *p, int targetCol)
{
	// Cases: queen's side castle or king's side castle
	assert(chess);
	assert(p);
	assert(targetCol == 6 || targetCol == 2);
	int rookStartCol;
	if (targetCol == 6)
	{
		// King's side
		rookStartCol = 7;
	}
	else
	{
		// Queen's side
		rookStartCol = 0;
	}
	NormalChessPiece *object = PiecesGetAt(chess->arrPieces, p->row, rookStartCol);
	return (NormalChessMove)
	{
		.subjectCol = p->col,
		.subjectRow = p->row,
		.objectCol  = object->col,
		.objectRow  = object->row,
		.targetCol  = targetCol,
		.targetRow  = p->row,
	};
}

// Returns: row of captured piece, if any, and returns negative otherwise.
NormalChessMove NormalChessCreatePawnMove(NormalChess *chess, NormalChessPiece *p, int targetCol,
		int targetRow)
{
	// Cases: capture move, en passant move, or first move is a double move.
	int dRow = targetRow - p->row;
	int dCol = targetCol - p->col;
	if (abs(dRow) == 2)
	{
		// First move is double move. Cannot be a capture.
		assert(!PiecesGetAt(chess->arrPieces, targetRow, targetCol));
		return (NormalChessMove)
		{
			.subjectCol = p->col,
			.subjectRow = p->row,
			.objectCol  = -1,
			.objectRow  = -1,
			.targetCol  = targetCol,
			.targetRow  = targetRow,
		};
	}
	else
	{
		// En-passant capture or normal capture.
		// It is en passant if the pawn is moving diagonal to capture and there is no
		// piece to capture at that target square.
		assert(dCol);
		NormalChessPiece *target = PiecesGetAt(chess->arrPieces, targetRow, targetCol);
		if (!target)
		{
			// En passant capture -> remove the other pawn which is next to this one
			target = PiecesGetAt(chess->arrPieces, p->row, targetCol);
		}
		assert(target);
		assert(p);
		return (NormalChessMove)
		{
			.subjectCol = p->col,
			.subjectRow = p->row,
			.objectCol  = target->col,
			.objectRow  = p->row,
			.targetCol  = targetCol,
			.targetRow  = targetRow,
		};
	}
}

// Handle normal moves and special moves like castling.
NormalChessMove NormalChessCreateMove(NormalChess *chess, int startCol, int startRow, int targetCol, 
		int targetRow)
{
	assert(chess);
	assert(chess->arrPieces);
	NormalChessPiece *p = PiecesGetAt(chess->arrPieces, startRow, startCol);
	assert(p);
	if (NormalChessSpecialMovesContains(chess, p, targetRow, targetCol))
	{
		// Special move.
		switch (p->kind)
		{
			case WHITE_KING:
			case BLACK_KING:
				// King's special move is castling.
				return NormalChessCreateCastleMove(chess, p, targetCol);
			case WHITE_PAWN:
			case BLACK_PAWN:
				// Pawn's speical move is a double move or en passant.
				return NormalChessCreatePawnMove(chess, p, targetCol, targetRow);
			default:
				assert(0 && "did not handle all special moves");
		}
	}
	else
	{
		// Normal move.
		assert(p);
		NormalChessPiece *obj = PiecesGetAt(chess->arrPieces, targetRow, targetCol);
		return (NormalChessMove)
		{
			.subjectCol = p->col,
			.subjectRow = p->row,
			.objectCol  = obj? obj->col : -1,
			.objectRow  = obj? obj->row : -1,
			.targetCol  = targetCol,
			.targetRow  = targetRow,
		};
	}
}

void NormalChessDoCastle(NormalChess *chess, NormalChessMove move)
{
	NormalChessPiece *p = NormalChessMoveGetSubject(move, chess->arrPieces);
	assert(p);
	assert(NormalChessSpecialMovesContains(chess, p, move.targetRow, move.targetCol));
	assert(0 && "not implemented yet");
}

void NormalChessDoPawnSpecial(NormalChess *chess, NormalChessMove move)
{
	NormalChessPiece *p = NormalChessMoveGetSubject(move, chess->arrPieces);
	assert(p);
	assert(NormalChessSpecialMovesContains(chess, p, move.targetRow, move.targetCol));
	if (move.targetCol != move.subjectCol)
	{
		// En Passant -> capture the adjacent pawn.
		PiecesRemovePieceAt(chess->arrPieces, move.subjectRow, move.targetCol);
	}
	else
	{
		// Double pawn move -> update the last double pawn column
		chess->doublePawnCol = move.subjectCol;
	}
}

// Update any flags that result from moving the king or rooks (for castling).
void NormalChessUpdateMovementFlags(NormalChess *chess, NormalChessMove move)
{
	NormalChessPiece *moveSubject = NormalChessMoveGetSubject(move, chess->arrPieces);
	assert(moveSubject);
	switch (moveSubject->kind)
	{
		case WHITE_KING:
			// King moved.
			chess->hasWhiteKingMoved = 1;
			break;
		case BLACK_KING:
			// King moved.
			chess->hasBlackKingMoved = 1;
			break;
		case WHITE_ROOK:
			// Rook moved.
			if (move.targetCol > move.subjectCol)
			{
				// King's side
				chess->hasWhiteKingsRookMoved = 1;
			}
			else
			{
				// Queen's side
				chess->hasWhiteQueensRookMoved = 1;
			}
			break;
		case BLACK_ROOK:
			// Rook moved.
			if (move.targetCol > move.subjectCol)
			{
				// King's side
				chess->hasBlackKingsRookMoved = 1;
			}
			else
			{
				// Queen's side
				chess->hasBlackQueensRookMoved = 1;
			}
			break;
		default:
			// No flags to update for other pieces.
			break;
	}
}

void NormalChessDoMove(NormalChess *chess, NormalChessMove move)
{
	assert(chess);
	assert(move.subjectCol >= 0 && move.subjectCol <= 7);
	assert(move.subjectRow >= 0 && move.subjectRow <= 7);
	NormalChessPiece *moveSubject = NormalChessMoveGetSubject(move, chess->arrPieces);
	assert(moveSubject);
	if (NormalChessSpecialMovesContains(chess, moveSubject, move.targetRow, move.targetCol))
	{
		// Special move.
		switch (moveSubject->kind)
		{
			case WHITE_KING:
			case BLACK_KING:
				// King's castling -> move the rook too.
				NormalChessDoCastle(chess, move);
				break;
			case WHITE_PAWN:
			case BLACK_PAWN:
				// En passant requires capturing the other pawn that was next to the subject.
				// Pawn's special move is a double move or en passant.
				NormalChessDoPawnSpecial(chess, move);
				break;
			default:
				assert(0 && "did not handle all special moves");
		}
	}
	NormalChessUpdateMovementFlags(chess, move);
	// The subject always moves/captures to the target spot.
	PiecesDoCapture(chess->arrPieces, moveSubject->row, moveSubject->col, move.targetRow, move.targetCol);
	// Next turn!
	chess->turn++;
}

// See if a piece is prevented from moving to a target square because it is pinned.
// TODO: check the case if the move is a capture, because this function is
// currently causing a bug where capturing is not allowed even if the capture
// un-pins the piece.
int PiecesIsPiecePinned(const NormalChessPiece **arrPieces, NormalChessPiece *p, int targetRow,
		int targetCol)
{
	assert(p);
	const NormalChessPiece *king = PiecesFindKing(arrPieces, p->kind);
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
	int isPinned = PiecesCanTeamCaptureSpot(arrPieces, NormalChessEnemyKingKind(PieceKingOf(p)),
			king->row, king->col);
	// Restore the pieces original position.
	p->row = originalRow;
	p->col = originalCol;
	return isPinned;
}

int NormalChessAllMovesContains(const NormalChess *c, NormalChessPiece *p, int row, int col)
{
	// Must be a square within the piece's normal moves or special moves.
	int normal = NormalChessMovesContains(p, row, col);
	int special = NormalChessSpecialMovesContains(c, p, row, col);
	const NormalChessPiece **arrPiecesConst = (const NormalChessPiece**) c->arrPieces;
	if (!normal && !special)
	{
		return 0;
	}
	// A piece cannot capture any pieces on the same team.
	const NormalChessPiece *other = PiecesGetAtConst(arrPiecesConst, row, col);
	if (other && NormalChessPieceTeamEq(p, other))
	{
		return 0;
	}
	// A sliding piece's moves are blocked by the first piece hit.
	// TODO: comment why is the !special is here again?
	if (!special && PiecesMoveIsBlocked(arrPiecesConst, p, row, col))
	{
		return 0;
	}
	// A piece may not move if it is pinned to the king
	if (PiecesIsPiecePinned(arrPiecesConst, p, row, col))
	{
		return 0;
	}
	// Exception: pawns cannot capture forward.
	if ((p->kind == WHITE_PAWN || p->kind == BLACK_PAWN)
			&& col == p->col
			&& PiecesGetAtConst(arrPiecesConst, row, col))
	{
		return 0;
	}
	return 1;
}

// Get a list of all valid moves for a piece.
// Returns: a NEW dynamic array of (col, row) which must be FREEd later.
// NOTE: if creating these dynamic lists of move squares is too slow, etc, then
// we can just keep a one-time-allocated array of booleans for whether each
// square on the board can be moved to.
Vector2 *NormalChessCreatePieceMoveList(const NormalChess *c, NormalChessPiece *p)
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

int NormalChessIsKingInCheck(NormalChess *chess)
{
	NormalChessKind currentKing = NormalChessCurrentKing(chess);
	const NormalChessPiece **arrPiecesConst = (const NormalChessPiece **) chess->arrPieces;
	const NormalChessPiece *king = PiecesFindKing(arrPiecesConst, currentKing);
	if (!king)
	{
		return 0;
	}
	return PiecesCanTeamCaptureSpot(arrPiecesConst, NormalChessEnemyKingKind(currentKing), king->row,
			king->col);
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
		|| !PiecesFindKing((const NormalChessPiece **)chess->arrPieces, WHITE_KING)
		|| !PiecesFindKing((const NormalChessPiece **)chess->arrPieces, BLACK_KING);
}

void SpriteMoveToNormalChessPiece(Sprite *s, const GameContext *game)
{
	assert(s);
	assert(s->data.kind == SK_NORMAL_CHESS_PIECE);
	assert(game);
	NormalChessPiece *p = s->data.as_normalChessPiece;
	int tileSize = game->tileSize;
	int x, y;
	NormalChessPosToScreen(p->row, p->col, game->boardOffset.x, game->boardOffset.y, tileSize, &x, &y);
	SpriteMoveCenter(s, x + tileSize/2, y + tileSize/2);
}

// Initially create the sprites for the pieces in a normal chess game.
Sprite *SpritesArrCreateNormalChess(GameContext *game)
{
	Sprite *arrSprites = NULL;
	int x0 = game->boardOffset.x;
	int y0 = game->boardOffset.y;
	int tileSize = game->tileSize;
	NormalChessPiece **arrPieces = game->normalChess->arrPieces;
	for (int i = 0; i < arrlen(arrPieces); i++)
	{
		NormalChessPiece *piece = arrPieces[i];
		assert(piece);
		Sprite new;
		new.data = (SpriteData){ .kind = SK_NORMAL_CHESS_PIECE, .as_normalChessPiece = piece };
		new.boundingBox = (Rectangle){ 0, 0, 16, 16};
		new.refTexture = &(game->texPieces);
		new.textureRect = NormalChessKindToTextureRect(piece->kind);
		SpriteMoveToNormalChessPiece(&new, game);
		arrpush(arrSprites, new);
	}
	return arrSprites;
}

// What to do when leaving/cleaning up the current game state.
void GameCleanupState(GameContext *game)
{
	assert(game);
	switch (game->state)
	{
		case GS_PLAY:
		case GS_PLAY_PROMOTE:
		case GS_GAME_OVER:
			// Free normal chess game
			assert(game->normalChess != NULL);
			NormalChessDestroy(game->normalChess);
			game->normalChess = NULL;
			// Free sprites array
			if (game->arrSprites)
			{
				arrfree(game->arrSprites);
				game->arrSprites = NULL;
			}
			// Free dyanamic moves array
			if (game->arrDraggedPieceMoves)
			{
				arrfree(game->arrDraggedPieceMoves);
				game->arrDraggedPieceMoves = NULL;
			}
			// Current piece is now invalid
			break;
		case GS_MAIN_MENU:
			break;
		default:
			assert(0 && "unhandled state");
	}
}

// What to do when switching FROM current state TO next state.
void GameLeaveState(GameContext *game, GameState next)
{
	assert(game);
	switch (game->state)
	{
		case GS_PLAY:
			if (!(next == GS_PLAY_PROMOTE || next == GS_GAME_OVER))
			{
				GameCleanupState(game);
			}
			break;
		case GS_PLAY_PROMOTE:
			if (next != GS_PLAY)
			{
				GameCleanupState(game);
			}
			break;
		case GS_GAME_OVER:
			GameCleanupState(game);
			break;
		case GS_MAIN_MENU:
			GameCleanupState(game);
			break;
		default:
			assert(0 && "unhandled state");
	}
}

// What to do when switch FROM previous state TO current state.
void GameEnterState(GameContext *game, GameState previous)
{
	assert(game);
	switch (game->state)
	{
		case GS_PLAY:
			if (previous == GS_PLAY_PROMOTE)
			{
				// Returning from in-game promotion.
				assert(game->normalChess);
			}
			else
			{
				// Initialize the play state.
				game->normalChess = NormalChessInit();
				// Initialize sprites from normal chess.
				assert(!game->arrSprites);
				game->arrSprites = SpritesArrCreateNormalChess(game);
			}
			break;
		case GS_PLAY_PROMOTE:
			break;
		case GS_GAME_OVER:
			break;
		case GS_MAIN_MENU:
			break;
		default:
			assert(0 && "unhandled state");
	}
}

void GameSwitchState(GameContext *game, GameState newState)
{
	GameLeaveState(game, newState);
	GameState previous = game->state;
	game->state = newState;
	GameEnterState(game, previous);
}

Rectangle GameGetBoardRect(const GameContext *game)
{
	const int boardWidth = 8;
	const int boardHeight = 8;
	return (Rectangle)
	{
		.x = game->boardOffset.x,
		.y = game->boardOffset.y,
		.width = boardWidth * game->tileSize,
		.height = boardHeight * game->tileSize,
	};
}

int GameIsPointOnBoard(const GameContext *game, Vector2 screenPos)
{
	return CheckCollisionPointRec(screenPos, GameGetBoardRect(game));
}

NormalChessPiece *GameGetPieceAt(const GameContext *game, Vector2 screenPos)
{
	int x0 = game->boardOffset.x;
	int y0 = game->boardOffset.y;
	int tileSize = game->tileSize;
	if (!GameIsPointOnBoard(game, screenPos))
	{
		return 0;
	}
	int row, col;
	ScreenToNormalChessPos(screenPos.x, screenPos.y, x0, y0, tileSize, &row, &col);
	return PiecesGetAt(game->normalChess->arrPieces, row, col);
}

// TODO: do we need to use this?
NormalChessPiece *GameGetValidSelectedPiece(const GameContext *game)
{
	assert(game);
	if (game->refSelectedSprite && game->refSelectedSprite->data.kind == SK_NORMAL_CHESS_PIECE)
	{
		NormalChessPiece *p = game->refSelectedSprite->data.as_normalChessPiece;
		if (NormalChessCanUsePiece(game->normalChess, p))
		{
			return p;
		}
	}
	return NULL;
}

// NOTE: this automatically frees the dynamic array (arrDraggedPieceMoves)
// if it is already pointing to something.
void UpdateMoveSquares(GameContext *game)
{
	assert(game);
	if (game->arrDraggedPieceMoves)
	{
		ClearMoveSquares(game);
	}
	assert(game->arrDraggedPieceMoves == NULL);
	NormalChessPiece *p = GameGetValidSelectedPiece(game);
	if (p)
	{
		Vector2 *newArrMoves = NormalChessCreatePieceMoveList(game->normalChess, p);
		game->arrDraggedPieceMoves = newArrMoves;
	}
}

NormalChessPiece *NormalChessMoveGetCapturedPiece(NormalChess *chess, NormalChessMove move)
{
	NormalChessPiece *moveSubject = NormalChessMoveGetSubject(move, chess->arrPieces);
	NormalChessPiece *moveObject = NormalChessMoveGetObject(move, chess->arrPieces);
	if (NormalChessSpecialMovesContains(chess, moveSubject, move.targetRow, move.targetCol))
	{
		// This move is special, so see what kind it is.
		assert(moveSubject);
		switch (moveSubject->kind)
		{
			case WHITE_KING:
			case BLACK_KING:
				// King castling
				return NULL;
			case WHITE_PAWN:
			case BLACK_PAWN:
				// En passant or double move
				return moveObject;
			default:
				assert(0 && "did not handle a special move case");
		}
	}
	else
	{
		return moveObject;
	}
}

// Move the selected piece to the target.
void GameDoMoveNormalChess(GameContext *game, int targetCol, int targetRow)
{
	assert(targetRow >= 0 && targetRow <= 7);
	assert(targetCol >= 0 && targetCol <= 7);
	assert(game);
	assert(game->normalChess);
	assert(game->refSelectedSprite);
	// Make sure that there is a piece to move.
	NormalChessPiece *p = GameGetValidSelectedPiece(game);
	assert(p);
	// Create the chess move that the user indicated.
	NormalChessMove theMove = NormalChessCreateMove(game->normalChess, p->col, p->row, targetCol,
			targetRow);
	// Remove the target sprite if it will be captured.
	NormalChessPiece *target = NormalChessMoveGetCapturedPiece(game->normalChess, theMove);
	if (target)
	{
		Sprite *targetSprite = SpritesArrFindNormalChessSpriteFor(game->arrSprites, target);
		assert(targetSprite);
		SpritesArrRemoveSprite(&game->arrSprites, targetSprite);
	}
	// Do chess game move and sprite move.
	NormalChessDoMove(game->normalChess, theMove);
	SpriteMoveToNormalChessPiece(game->refSelectedSprite, game);
	// De-select the selected sprite and remove highlights.
	game->refSelectedSprite = NULL;
	UpdateMoveSquares(game);
}

void UpdatePlay(GameContext *game)
{
	Vector2 mousePos = GetMousePosition();
	const int drag = 10; // minimum dx or dy for considering a mouse motion while clicked as a drag.
	if (IsMouseButtonPressed(0))
	{
		// Handle mouse first pressed.
		if (GameIsPointOnBoard(game, mousePos))
		{
			int col, row;
			ScreenToNormalChessPos(mousePos.x, mousePos.y, game->boardOffset.x, game->boardOffset.y,
					game->tileSize, &row, &col);
			Vector2 mouseSquare = (Vector2){ col, row };
			// Otherwise check for click on a valid piece.
			if (!(game->refSelectedSprite && Vector2ArrFind(game->arrDraggedPieceMoves, mouseSquare)))
			{
				Sprite *s = SpritesArrFindNormalChessSpriteAt(game->arrSprites, col, row);
				if (s && NormalChessCanUsePiece(game->normalChess, s->data.as_normalChessPiece))
				{
					game->refSelectedSprite = s;
				}
				else
				{
					game->refSelectedSprite = NULL;
				}
				UpdateMoveSquares(game);
			}
		}
	}
	else if (IsMouseButtonReleased(0))
	{
		// TODO: handle mouse release.
		if (game->refSelectedSprite)
		{
			SpriteMoveToNormalChessPiece(game->refSelectedSprite, game);
			int col, row;
			ScreenToNormalChessPos(mousePos.x, mousePos.y, game->boardOffset.x, game->boardOffset.y,
					game->tileSize, &row, &col);
			Vector2 mouseSquare = (Vector2){ col, row };
			if (Vector2ArrFind(game->arrDraggedPieceMoves, mouseSquare))
			{
				// Released mouse over a valid movement square for the piece.
				GameDoMoveNormalChess(game, col, row);
				assert(!game->refSelectedSprite);
				assert(!game->arrDraggedPieceMoves);
			}
		}
	}
	else if (IsMouseButtonDown(0))
	{
		if (game->refSelectedSprite)
		{
			// Move the current sprite if the mouse is far enough away.
			int x, y;
			int row = game->refSelectedSprite->data.as_normalChessPiece->row;
			int col = game->refSelectedSprite->data.as_normalChessPiece->col;
			NormalChessPosToScreen(row, col, game->boardOffset.x, game->boardOffset.y, game->tileSize,
					&x, &y);
			Vector2 originalPos = (Vector2){ x + game->tileSize/2, y + game->tileSize/2 };
			if (Vector2DistanceSquared(mousePos, originalPos) >= drag)
			{
				SpriteMoveCenter(game->refSelectedSprite, mousePos.x, mousePos.y);
			}
		}
	}
}

void UpdatePlayPromote(GameContext *game)
{
	if (0)
	{
		// Done promoting, go back to play
		GameSwitchState(game, GS_PLAY);
	}
}

void UpdateGameOver(GameContext *game)
{
	if (0)
	{
		// Player chose to play again.
		GameSwitchState(game, GS_PLAY);
	}
	else if (0)
	{
		// Player chose to return to menu.
		GameSwitchState(game, GS_MAIN_MENU);
	}
}

void UpdateMainMenu(GameContext *game)
{
	// TODO: implement menu
	if (game->ticks >= 30)
	{
		GameSwitchState(game, GS_PLAY);
	}
}

void UpdateDebug(GameContext *game)
{
	if (IsKeyReleased(KEY_ZERO))
	{
		game->isDebug = 0;
	}
	else if (IsKeyReleased(KEY_EQUAL))
	{
		game->isDebug++;
	}
	else if (IsKeyReleased(KEY_MINUS))
	{
		// Don't allow isDebug to go negative.
		if (game->isDebug > 0)
		{
			game->isDebug--;
		}
	}
}

void Update(GameContext *game) {
	UpdateDebug(game);
	switch (game->state)
	{
		case GS_PLAY:
			UpdatePlay(game);
			break;
		case GS_PLAY_PROMOTE:
			UpdatePlayPromote(game);
			break;
		case GS_GAME_OVER:
			UpdateGameOver(game);
			break;
		case GS_MAIN_MENU:
			UpdateMainMenu(game);
			break;
		case GS_NONE:
			assert(0 && "game->state should never have the value of GS_NONE");
	}
	game->ticks++;
}

// Draw a slice of a texture centered in the bounds rectangle.
void DrawTextureRecCentered(Texture2D tex, Rectangle slice, Rectangle bounds)
{
	int x = bounds.x + (bounds.width - slice.width)/2;
	int y = bounds.y + (bounds.height - slice.height)/2;
	DrawTextureRec(tex, slice, (Vector2){ x, y }, WHITE);
}

void DrawSprite(const GameContext *game, const Sprite *s)
{
	assert(game);
	assert(s);
	switch (s->data.kind)
	{
		case SK_NORMAL_CHESS_PIECE:
			DrawTextureRecCentered(*s->refTexture,
					NormalChessKindToTextureRect(s->data.as_normalChessPiece->kind),
					s->boundingBox);
			break;
		default:
			assert(0 && "not implemented");
	}
	// Debug draw bounding box
	if (game->isDebug >= 3)
	{
		DrawRectangleLinesEx(s->boundingBox, 1, WHITE);
	}
}

void DrawPlay(const GameContext *game)
{
	assert(game);
	assert(game->normalChess);
	int x0 = game->boardOffset.x;
	int y0 = game->boardOffset.y;
	int tileSize = game->tileSize;
	ClearBackground(DARKGREEN);
	DrawChessBoard(x0, y0, tileSize, 8, 8);
	// Draw move highlight squares.
	for (int i = 0; i < arrlen(game->arrDraggedPieceMoves); i++)
	{
		Vector2 pos = game->arrDraggedPieceMoves[i];
		int x, y;
		NormalChessPosToScreen(pos.y, pos.x, x0, y0, tileSize, &x, &y);
		DrawRectangle(x, y, tileSize, tileSize, HI_COLOR);
	}
	// Draw selected piece highlight square.
	if (game->refSelectedSprite)
	{
		const NormalChessPiece *p = game->refSelectedSprite->data.as_normalChessPiece;
		if (p)
		{
			int x, y;
			NormalChessPosToScreen(p->row, p->col, x0, y0, tileSize, &x, &y);
			DrawRectangle(x, y, tileSize, tileSize, SELECT_COLOR);
		}
	}
	// Draw sprites
	for (int i = 0; i < arrlen(game->arrSprites); i++)
	{
		DrawSprite(game, &game->arrSprites[i]);
	}
	// Debug info
	if (game->isDebug)
	{
		// selectedPiece
		if (game->isDebug >= 3)
		{
			DrawText(TextFormat("selectedPiece: %p", GameGetValidSelectedPiece(game)),
					190, 20, 20, WHITE);
		}
		// draw list of game pieces
		if (game->isDebug >= 6)
		{
			char msg[50];
			int scroll = -2 * (game->ticks % 100);
			for (int i = 0; i < arrlen(game->normalChess->arrPieces); i++)
			{
				NormalChessPiece *p = game->normalChess->arrPieces[i];
				snprintf(msg, sizeof(msg), "#%2d: %s at row:%2d, col:%2d",
						i, NormalChessKindToStr(p->kind), p->row, p->col);
				DrawText(msg, 180, 30 + scroll + i * 16, 20, WHITE);
			}
		}
		// Normal chess debug
		if (game->isDebug >= 4)
		{
			char msg[100];
			int x1 = 15, y1 = 5;
			snprintf(msg, sizeof(msg), "hasWhiteKingMoved:%d", game->normalChess->hasWhiteKingMoved);
			DrawText(msg, x1, y1, 17, WHITE);
			snprintf(msg, sizeof(msg), "hasWhiteKingsRookMoved:%d",
					game->normalChess->hasWhiteKingsRookMoved);
			DrawText(msg, x1, y1 + 17, 16, WHITE);
			snprintf(msg, sizeof(msg), "hasWhiteQueensRookMoved:%d",
					game->normalChess->hasWhiteQueensRookMoved);
			DrawText(msg, x1, y1 + 17*2, 16, WHITE);
			snprintf(msg, sizeof(msg), "hasBlackKingMoved:%d", game->normalChess->hasBlackKingMoved);
			DrawText(msg, x1, y1 + 17*3, 16, WHITE);
			snprintf(msg, sizeof(msg), "hasBlackKingsRookMoved:%d",
					game->normalChess->hasBlackKingsRookMoved);
			DrawText(msg, x1, y1 + 17*4, 16, WHITE);
			snprintf(msg, sizeof(msg), "hasBlackQueensRookMoved:%d",
					game->normalChess->hasBlackQueensRookMoved);
			DrawText(msg, x1, y1 + 17*5, 16, WHITE);
		}
	}
}

void DrawGameOver(const GameContext *game)
{
	DrawPlay(game);
	DrawText("Game over", 20, 50, 16, RED);
}

void DrawMainMenu(const GameContext *game)
{
	DrawText("Menu", 20, 50, 16, SKYBLUE);
	Rectangle slice = (Rectangle){ 0, 0, 160, 64 };
	Vector2 pos = (Vector2){ 250, 200 };
	DrawTextureRec(game->texPieces, slice, pos, WHITE);
}

void DrawDebug(const GameContext *game)
{
	if (!game->isDebug)
	{
		return;
	}
	// Display the current debug level
	DrawText(TextFormat("debug level: %d", game->isDebug), 0, 0, 16, GREEN);
	if (game->isDebug >= 3)
	{
		// Current state
		DrawText(TextFormat("game state: %s", GameStateToStr(game->state)), 10, 10, 20, GREEN);
	}
	if (game->isDebug >= 4)
	{
		// Tick count
		DrawText(TextFormat("game ticks: %d", game->ticks), 10, 36, 20, GREEN);
	}
}

void Draw(const GameContext *game) {
	switch (game->state)
	{
		case GS_PLAY:
			DrawPlay(game);
			break;
		case GS_GAME_OVER:
			DrawGameOver(game);
			break;
		case GS_MAIN_MENU:
			DrawMainMenu(game);
			break;
		default:
			// Unknown game state
			break;
	}
	DrawDebug(game);
}

void GameCleanup(GameContext *game)
{
	GameCleanupState(game);
	// Make sure every pointer has been dealt with
	assert(game->normalChess == NULL);
	assert(game->arrDraggedPieceMoves == NULL);
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
		.isDebug              = 0, // integer for game debug flag, higher number means more debug info
		.state                = GS_MAIN_MENU,
		.ticks                = 0,
		.normalChess          = NULL,
		.boardOffset          = (Vector2) { 160, 110 },
		.tileSize             = TEXTURE_TILE_SIZE * 2,
		.arrDraggedPieceMoves = NULL,
		.refSelectedSprite    = NULL,
		.arrSprites           = NULL,
		.texPieces            = LoadTexture("gfx/pieces.png"),
		.texBoard             = LoadTexture("gfx/board.png"),
		.texGUI               = LoadTexture("gfx/gui.png"),
	};
	GameEnterState(&game, GS_NONE);
	// Main loop:
    while (!WindowShouldClose()) {
        Update(&game);
        BeginDrawing();
        Draw(&game);
        EndDrawing();
    }
	// Clean up the game
	GameCleanup(&game);
	CloseWindow();
    return 0;
}

