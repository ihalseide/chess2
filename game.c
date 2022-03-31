#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include "raylib.h"
#include "stb_ds.h"
#include "tilemap.h"
#include "game.h"

#define abs(x) (((x) > 0)? (x) : -(x))
#define sign(x) ((x)? (((x) > 0)? 1 : -1) : 0)

// TODO: add detection of game-over.
// TODO: add animation of pieces moving.
// TODO: add gameplay buttons to quit, resign, restart, etc..
// TODO: add game turn timers.
// TODO: add sound effects: checkMate, resign, game over.
// TODO: add particles.
// TODO: add music.

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

int SpriteKindIsUI(SpriteKind k)
{
	switch (k)
	{
		case SK_GENERIC_BUTTON:
		case SK_PROMOTE_BUTTON:
			return 1;
		case SK_NORMAL_CHESS_PIECE:
		case SK_NONE:
			return 0;
		default:
			assert(0 && "unhandled SpriteKind");
	}
}

int SpriteIsUI(Sprite *s)
{
	return s && SpriteKindIsUI(s->data.kind);
}

const char *SpriteKindToStr(SpriteKind k)
{
	switch (k)
	{
		case SK_NONE:               return "SK_NONE";
		case SK_PROMOTE_BUTTON:     return "SK_PROMOTE_BUTTON";
		case SK_GENERIC_BUTTON:     return "SK_GENERIC_BUTTON";
		case SK_NORMAL_CHESS_PIECE: return "SK_NORMAL_CHESS_PIECE";
		default:
			return "(invalid SpriteKind)";
	}
}

const char *GameStateToStr(GameState s)
{
	_Static_assert(_GS_COUNT == 6, "exhaustive handling of all GameState's");
	switch (s)
	{
		case GS_NONE:         return "GS_NONE";
		case GS_PLAY:         return "GS_PLAY";
		case GS_PLAY_ANIMATE: return "GS_PLAY_ANIMATE";
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
			assert(0 && "invalid NormalChessKind");
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
		arrput(pieces, p);
		p = NormalChessPieceAlloc(BLACK_PAWN, 6, col);
		arrput(pieces, p);
	}
	// White pieces
	p = NormalChessPieceAlloc(WHITE_ROOK, 0, 0);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(WHITE_KNIGHT, 0, 1);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(WHITE_BISHOP, 0, 2);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(WHITE_QUEEN, 0, 3);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(WHITE_KING, 0, 4);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(WHITE_BISHOP, 0, 5);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(WHITE_KNIGHT, 0, 6);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(WHITE_ROOK, 0, 7);
	arrput(pieces, p);
	// Black pieces
	p = NormalChessPieceAlloc(BLACK_ROOK, 7, 0);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(BLACK_KNIGHT, 7, 1);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(BLACK_BISHOP, 7, 2);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(BLACK_QUEEN, 7, 3);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(BLACK_KING, 7, 4);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(BLACK_BISHOP, 7, 5);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(BLACK_KNIGHT, 7, 6);
	arrput(pieces, p);
	p = NormalChessPieceAlloc(BLACK_ROOK, 7, 7);
	arrput(pieces, p);
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

int PiecesCountAtConst(const NormalChessPiece **arrPieces, int row, int col)
{
	int count = 0;
	for (int i = 0; i < arrlen(arrPieces); i++)
	{
		const NormalChessPiece *p = arrPieces[i];
		if (p->row == row && p->col == col)
		{
			count++;
		}
	}
	return count;
}

NormalChessPiece *NormalChessGetPawnPromotion(NormalChess *chess)
{
	assert(chess);
	for (int i = 0; i < arrlen(chess->arrPieces); i++)
	{
		NormalChessPiece *p = chess->arrPieces[i];
		if (NormalChessCanUsePiece(chess, p))
		{
			// White pawn must reach row 7.
			// Black pawn must reach row 0.
			if ((p->kind == WHITE_PAWN && p->row == 7) || (p->kind == BLACK_PAWN && p->row == 0))
			{
				return p;
			}
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
void PiecesDoMove(NormalChessPiece **arrPieces, int startRow, int startCol, int targetRow, int targetCol)
{
	// There should not be a piece at the target location.
	assert(!PiecesGetAt(arrPieces, targetRow, targetCol));
	// Find the piece in the array at the location and move it
	NormalChessPiece *p = PiecesGetAt(arrPieces, startRow, startCol);
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
int PiecesMoveIsBlocked(const NormalChessPiece **arrPieces, const NormalChessPiece *p, int targetRow,
		int targetCol)
{
	assert(arrPieces);
	assert(p);
	// If there is another piece on the same square as the given piece, then
	// the piece is considered blocked. This is only the case for checking if
	// a piece is pinned and we want to simulate a capture without affecting
	// the other pieces.
	if (PiecesCountAtConst(arrPieces, p->row, p->col) > 1)
	{
		return 1;
	}
	switch (p->kind)
	{
		case WHITE_PAWN:
		case BLACK_PAWN:
			{
				// Pawn is blocked for diagonal moves if there is no piece for it to capture at the
				// square. Pawn is also blocked for forward moves if there is a piece blocking,
				// because it cannot capture forwards.
				const NormalChessPiece *targetP = PiecesGetAtConst(arrPieces, targetRow, targetCol);
				return (targetCol != p->col && !targetP) || (targetCol == p->col && targetP);
			}
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
			if (p->row == 1 && dRow == 2 && dCol == 0
					&& !PiecesGetAtConst(arrPiecesConst, p->row + 1, p->col)
					&& !PiecesGetAtConst(arrPiecesConst, p->row + 2, p->col))
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
			if (p->row == 6 && dRow == -2 && dCol == 0
					&& !PiecesGetAtConst(arrPiecesConst, p->row - 1, p->col)
					&& !PiecesGetAtConst(arrPiecesConst, p->row - 2, p->col))
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
						&& PiecesGetAtConst(arrPiecesConst, p->row, 7) // must be rook piece
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
						&& PiecesGetAtConst(arrPiecesConst, p->row, 0) // must be rook piece
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
					&& PiecesGetAtConst(arrPiecesConst, p->row, 7) // must be rook piece
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
					&& PiecesGetAtConst(arrPiecesConst, p->row, 0) // must be rook piece
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

// Do castle move.
void NormalChessDoCastle(NormalChess *chess, NormalChessMove move)
{
	NormalChessPiece *king = NormalChessMoveGetSubject(move, chess->arrPieces);
	assert(king);
	assert(NormalChessSpecialMovesContains(chess, king, move.targetRow, move.targetCol));
	NormalChessPiece *rook = NormalChessMoveGetObject(move, chess->arrPieces);
	assert(rook);
	// Move the castle (because the king is moved normally in another function).
	int rookTargetCol;
	if (move.objectCol > move.subjectCol)
	{
		// King's-side rook
		rookTargetCol = move.targetCol - 1;
		// Update this additional movement flag for this rook.
		switch (king->kind)
		{
			case WHITE_KING:
				chess->hasWhiteKingsRookMoved = 1;
				break;
			case BLACK_KING:
				chess->hasBlackKingsRookMoved = 1;
				break;
			default:
				assert(0 && "unreachable");
		}
	}
	else
	{
		// Queen's-side rook
		rookTargetCol = move.targetCol + 1;
		// Update this additional movement flag for this rook.
		switch (king->kind)
		{
			case WHITE_KING:
				chess->hasWhiteQueensRookMoved = 1;
				break;
			case BLACK_KING:
				chess->hasBlackQueensRookMoved = 1;
				break;
			default:
				assert(0 && "unreachable");
		}
	}
	PiecesDoMove(chess->arrPieces, move.objectRow, move.objectCol, move.objectRow, rookTargetCol);
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
	// If the subject moves.
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
	// If a rook is captured, it is considered to have moved so that castling
	// is no longer possible with that rook.
	NormalChessPiece *moveObject = NormalChessMoveGetObject(move, chess->arrPieces);
	if (moveObject)
	{
		switch (moveObject->kind)
		{
			case WHITE_ROOK:
				// Rook was captured.
				if (move.objectCol > 4)
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
				// Rook was captured.
				if (move.objectCol > 4)
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
	// Do not increment to next turn yet
}

// See if a piece is prevented from moving to a target square because it is pinned.
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
	// If this current piece moves to a square where one of the enemy pieces is, the enemy
	// piece is considered to be blocked (the move is acting like a capture). 
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
				arrput(result, colRow);
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
		arrput(arrSprites, new);
	}
	return arrSprites;
}

// What to do when leaving/cleaning up the current game state.
void GameCleanupState(GameContext *game)
{
	assert(game);
	_Static_assert(_GS_COUNT == 6, "exhaustive handling of all GameState's");
	switch (game->state)
	{
		case GS_PLAY:
		case GS_PLAY_ANIMATE:
		case GS_PLAY_PROMOTE:
		case GS_GAME_OVER:
			// Free normal chess game
			assert(game->normalChess != NULL);
			NormalChessDestroy(game->normalChess);
			game->normalChess = NULL;
			// Free background tilemap
			assert(game->tmapBackground);
			TileMapComponentFree(game->tmapBackground);
			game->tmapBackground = NULL;
			// Free board tilemap
			assert(game->tmapBoard);
			TileMapComponentFree(game->tmapBoard);
			game->tmapBoard = NULL;
			// Free sprites array
			if (game->arrSprites)
			{
				// Note: assuming that no sprite "owns" any pointers.
				arrfree(game->arrSprites);
				game->arrSprites = NULL;
			}
			// Free UI sprites array
			if (game->arrUISprites)
			{
				// Note: assuming that no sprite "owns" any pointers.
				arrfree(game->arrUISprites);
				game->arrUISprites = NULL;
			}
			// Free dyanamic moves array
			if (game->arrDraggedPieceMoves)
			{
				arrfree(game->arrDraggedPieceMoves);
				game->arrDraggedPieceMoves = NULL;
			}
			// Current piece is now invalid
			game->refSelectedSprite = NULL;
			break;
		case GS_MAIN_MENU:
			break;
		case GS_NONE:
			// Nothing to do
			break;
		default:
			assert(0 && "unhandled state");
	}
}

// Meant to be called by GameLeaveState.
void GameLeaveStatePlay(GameContext *game, GameState next)
{
	assert(game);
	switch (next)
	{
		case GS_PLAY_PROMOTE:
		case GS_PLAY_ANIMATE:
		case GS_GAME_OVER:
			// Do nothing
			break;
		default:
			GameCleanupState(game);
			break;
	}
}

// Meant to be called by GameLeaveState.
void GameLeaveStatePlayPromote(GameContext *game, GameState next)
{
	if (next == GS_PLAY)
	{
		// Free the promote button sprites. Changes the arrUISprites len!
		for (int i = 0; i < arrlen(game->arrUISprites); i++)
		{
			Sprite s = game->arrUISprites[i];
			if (s.data.kind == SK_PROMOTE_BUTTON)
			{
				arrdelswap(game->arrUISprites, i);
				i--;
			}
		}
	}
	else
	{
		GameCleanupState(game);
	}
}

// Meant to be called by GameLeaveState.
void GameLeaveStatePlayAnimate(GameContext *game, GameState next)
{
	if (next != GS_PLAY)
	{
		GameCleanupState(game);
	}
}

// Meant to be called by GameLeaveState.
void GameLeaveStateGameOver(GameContext *game, GameState next)
{
	GameCleanupState(game);
}

// Meant to be called by GameLeaveState.
void GameLeaveStateMainMenu(GameContext *game, GameState next)
{
	GameCleanupState(game);
}

// What to do when switching FROM current state TO next state.
void GameLeaveState(GameContext *game, GameState next)
{
	assert(game);
	_Static_assert(_GS_COUNT == 6, "exhaustive handling of all GameState's");
	switch (game->state)
	{
		case GS_PLAY:
			GameLeaveStatePlay(game, next);
			break;
		case GS_PLAY_ANIMATE:
			GameLeaveStatePlayAnimate(game, next);
			break;
		case GS_PLAY_PROMOTE:
			GameLeaveStatePlayPromote(game, next);
			break;
		case GS_GAME_OVER:
			GameLeaveStateGameOver(game, next);
			break;
		case GS_MAIN_MENU:
			GameLeaveStateMainMenu(game, next);
			break;
		case GS_NONE:
			assert(0 && "unhandled state");
	}
}

// Enter play promote state.
// Meant to be called by GameEnterState.
void GameEnterStatePlayPromote(GameContext *game, GameState previous)
{
	assert(previous == GS_PLAY);
	assert(game->normalChess);
	PlaySound(game->soundEnterPromote);
	const int menuWidth = 170; // px
	const int buttonWidth = 60; // px
	const int buttonHeight = 40; // px
	const int y0 = 32; // px
	const int y1 = 20; // px
	const int gapY = 5; // px
	const int numOptions = 4; // number of promotion pieces to choose from
	const int teamOffsetY = 40; // px
	// Initialize promotion menu.
	// Note that the menu's Y position moves down for when the black team is promoting because
	// the piece is further down on the screen than for the white team.
	NormalChessKind currentKing = NormalChessCurrentKing(game->normalChess);
	game->promotionMenuRect = (Rectangle)
	{
		game->boardOffset.x + game->tileSize * 8 + 10,
		game->boardOffset.y + ((currentKing == WHITE_KING)? 0 : teamOffsetY),
		menuWidth,
		y0 + (buttonHeight + gapY) * numOptions + y1,
	};
	// Initialize promotion menu buttons
	for (int i = 0; i < numOptions; i++)
	{
		NormalChessKind k = currentKing + 1 + i;
		Sprite button = (Sprite)
		{
			.data = (SpriteData)
			{
				.kind = SK_PROMOTE_BUTTON,
				.as_promoteButton = (PiecePromoteButton)
				{
					.pieceKind = k,
					.state = BS_ENABLED
				},
			},
			.refTexture = &game->texPieces,
			.textureRect = NormalChessKindToTextureRect(k),
			.boundingBox = (Rectangle)
			{
				.x = game->promotionMenuRect.x + (game->promotionMenuRect.width / 2) - (buttonWidth / 2),
				.y = game->promotionMenuRect.y + y0 + (buttonHeight + gapY) * i,
				.width = buttonWidth,
				.height = buttonHeight,
			},
		};
		arrput(game->arrUISprites, button);
	}
	// Use refSelectedSprite to refer to the pawn to promote.
	NormalChessPiece *promoteP = NormalChessGetPawnPromotion(game->normalChess);
	game->refSelectedSprite = SpritesArrFindNormalChessSpriteFor(game->arrSprites, promoteP);
}

void PlayInitBackgroundTiles(GameContext *game)
{
	const int mapCols = 19;
	const int mapRows = 15;
	const int tileSize = game->tileSize;
	const int x0 = 0;
	const int y0 = 0;
	assert(game);
	assert(game->tmapBoard == NULL);
	// Create empty tilemap
	game->tmapBackground = TileMapComponentAlloc(x0, y0, tileSize, mapCols, mapRows);
	// Fill with a single tile
	TileInfo tile = (TileInfo)
	{
		.refTexture = &game->texBoard,
	};
	// Set the initial tile ids to avoid doing it for every single location.
	tile.x0 = 160;
	tile.y0 = 32;
	int id1 = TileMapComponentSet(game->tmapBackground, 0, 0, tile);
	// Set the rest of the tiles to be the same
	for (int col = 0; col < mapCols; col++)
	{
		for (int row = 0; row < mapRows; row++)
		{
			int *loc = TileMapGet(game->tmapBackground->map, col, row);
			assert(loc);
			*loc = id1;
		}
	}
}

void PlayInitBoardTiles(GameContext *game)
{
	const int mapCols = 11;
	const int mapRows = 11;
	const int tileSize = game->tileSize;
	const int x0 = game->boardOffset.x - tileSize * 2;
	const int y0 = game->boardOffset.y - tileSize * 1;
	assert(game);
	assert(game->tmapBoard == NULL);
	// Create empty tilemap
	game->tmapBoard = TileMapComponentAlloc(x0, y0, tileSize, mapCols, mapRows);
	int row, col;
	TileInfo tile = (TileInfo) { .refTexture = &game->texBoard };
	// Top-left corner
	col = 1;
	row = 0;
	tile.x0 = 0;
	tile.y0 = 0;
	TileMapComponentSet(game->tmapBoard, col, row, tile);
	// Top row
	tile.x0 = tileSize;
	tile.y0 = 0;
	for (int i = 0; i < 8; i++)
	{
		col = 2 + i;
		row = 0;
		TileMapComponentSet(game->tmapBoard, col, row, tile);
	}
	// Top-right corner
	col = 10;
	row = 0;
	tile.x0 = tileSize * 2;
	tile.y0 = 0;
	TileMapComponentSet(game->tmapBoard, col, row, tile);
	// Right column
	tile.x0 = tileSize * 2;
	tile.y0 = tileSize;
	for (int i = 0; i < 8; i++)
	{
		col = 10;
		row = 1 + i;
		TileMapComponentSet(game->tmapBoard, col, row, tile);
	}
	// Bottom-right corner
	col = 10;
	row = 9;
	tile.x0 = tileSize * 2;
	tile.y0 = tileSize * 2;
	TileMapComponentSet(game->tmapBoard, col, row, tile);
	// Bottom row
	row = 9;
	tile.x0 = tileSize;
	tile.y0 = tileSize * 2;
	for (int i = 0; i < 8; i++)
	{
		col = 2 + i;
		// Extra range check
		if (col >= game->tmapBoard->map->columns)
		{
			break;
		}
		TileMapComponentSet(game->tmapBoard, col, row, tile);
	}
	// Bottom-left corner
	col = 1;
	row = 9;
	tile.x0 = 0;
	tile.y0 = tileSize * 2;
	TileMapComponentSet(game->tmapBoard, col, row, tile);
	// Left column
	tile.x0 = 0;
	tile.y0 = tileSize;
	col = 1;
	for (int i = 0; i < 8; i++)
	{
		row = 1 + i;
		TileMapComponentSet(game->tmapBoard, col, row, tile);
	}
	// Row labels
	tile.y0 = tileSize * 4;
	col = 0;
	for (int i = 0; i < 8; i++)
	{
		row = 1 + i;
		tile.x0 = (7 - i) * tileSize;
		TileMapComponentSet(game->tmapBoard, col, row, tile);
	}
	// Column labels
	tile.y0 = tileSize * 3;
	row = 10;
	for (int i = 0; i < 8; i++)
	{
		col = 2 + i;
		tile.x0 = i * tileSize;
		TileMapComponentSet(game->tmapBoard, col, row, tile);
	}
	// Chess board checkered tiles
	tile.y0 = 0;
	TileInfo light, dark;
	light = tile;
	light.x0 = 96;
	dark = tile;
	dark.x0 = 128;
	for (int row = 0; row < 8; row++)
	{
		for (int col = 0; col < 8; col++)
		{
			int tCol = col + 2;
			int tRow = row + 1;
			if (row % 2 == col % 2)
			{
				TileMapComponentSet(game->tmapBoard, tCol, tRow, light);
			}
			else
			{
				TileMapComponentSet(game->tmapBoard, tCol, tRow, dark);
			}
		}
	}
}

// Meant to be called by GameEnterState.
void GameEnterStatePlay(GameContext *game, GameState previous)
{
	// Enter play state.
	if (previous == GS_PLAY_PROMOTE || previous == GS_PLAY_ANIMATE)
	{
		// Returning from in-game promotion or animation.
		// TODO: check for game over
		// TODO: play sounds here
		// PlaySound(game->soundPromote);

		// This is where the turn is incremented
		game->normalChess->turn++;
		if (NormalChessIsGameOver(game->normalChess))
		{
			// If the game is over, switch states.
			GameSwitchState(game, GS_GAME_OVER);
			return;
		}
	}
	else
	{
		// Initialize the play state.
		game->boardOffset = (Vector2) { 160, 110 };
		game->normalChess = NormalChessInit();
		game->arrDraggedPieceMoves = NULL;
		game->refSelectedSprite = NULL;
		game->arrSprites = NULL;
		// Initialize the tile maps.
		PlayInitBackgroundTiles(game);
		PlayInitBoardTiles(game);
		// Initialize game sprites from normal chess pieces.
		assert(!game->arrSprites);
		game->arrSprites = SpritesArrCreateNormalChess(game);
		// Initialize the button sprites.
		SpriteData defaultData = (SpriteData)
		{
			.kind = SK_GENERIC_BUTTON,
			.as_genericButton = (GenericButton){0},
		};
		defaultData.as_genericButton.state = BS_ENABLED;
		Sprite menuButton = (Sprite)
		{
			.refTexture = &game->texGUI,
			.textureRect = (Rectangle){ 0, 0, 16, 16 },
			.boundingBox = (Rectangle){ 10, 10, 70, 35 },
			.data = defaultData,
		};
		menuButton.data.as_genericButton.refText = "Quit";
		arrput(game->arrUISprites, menuButton);
	}
}

// Meant to be called by GameEnterState.
void GameEnterStatePlayAnimate(GameContext *game, GameState previous)
{
	assert(previous == GS_PLAY);
	// TODO: setup for actually animating the pieces.
}

// Meant to be called by GameEnterState.
void GameEnterStateGameOver(GameContext *game, GameState previous)
{
	assert(previous == GS_PLAY);
	assert(0 && "not implemented yet");
}

// Meant to be called by GameEnterState.
void GameEnterStateMainMenu(GameContext *game, GameState previous)
{
	// Nothing to do.
}

// What to do when switch FROM previous state TO current state.
void GameEnterState(GameContext *game, GameState previous)
{
	assert(game);
	// Reset state tick timer
	game->stateTicks = 0;
	_Static_assert(_GS_COUNT == 6, "exhaustive handling of all GameState's");
	switch (game->state)
	{
		case GS_PLAY:
			GameEnterStatePlay(game, previous);
			break;
		case GS_PLAY_ANIMATE:
			GameEnterStatePlayAnimate(game, previous);
			break;
		case GS_PLAY_PROMOTE:
			GameEnterStatePlayPromote(game, previous);
			break;
		case GS_GAME_OVER:
			GameEnterStateGameOver(game, previous);
			break;
		case GS_MAIN_MENU:
			GameEnterStateMainMenu(game, previous);
			break;
		case GS_NONE:
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

// Does: get info about whether a chess move is a capture and what the object (acted-upon piece) is.
// Returns values through object and isCapture.
NormalChessPiece *NormalChessMoveGetObjectInfo(NormalChess *chess, NormalChessMove move, 
		NormalChessPiece **object, int *isCapture, int *isCastle)
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
				if (isCapture) { *isCapture = 0; }
				if (isCastle)  { *isCastle = 1; }
				if (object)    { *object = moveObject; }
				break;
			case WHITE_PAWN:
			case BLACK_PAWN:
				// En passant or double move
				if (isCapture) { *isCapture = move.targetCol != move.subjectCol; }
				if (isCastle)  { *isCastle = 0; }
				if (object)    { *object = moveObject; }
				break;
			default:
				assert(0 && "did not handle a special move case");
				break;
		}
	}
	else
	{
		// Normal move case:
		if (object)    { *object = moveObject; }
		if (isCastle)  { *isCastle = 0; }
		if (isCapture) { *isCapture = (moveObject != NULL); }
	}
}

// Move the selected piece to the target. Also resets the handledCheck flag to 0.
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
	// Create move info for handling the sprites after doing the chess move.
	NormalChessPiece *object;
	int isCapture, isCastle;
	NormalChessMoveGetObjectInfo(game->normalChess, theMove, &object, &isCapture, &isCastle);
	// Do chess game move and sprite move.
	NormalChessDoMove(game->normalChess, theMove);
	SpriteMoveToNormalChessPiece(game->refSelectedSprite, game);
	// Handle the sprites now.
	if (object)
	{
		Sprite *objectSprite = SpritesArrFindNormalChessSpriteFor(game->arrSprites, object);
		if (isCapture)
		{
			// Delete sprite for the object.
			assert(objectSprite);
			SpritesArrRemoveSprite(&game->arrSprites, objectSprite);
		}
		else
		{
			// Move sprite for the object.
			SpriteMoveToNormalChessPiece(objectSprite, game);
		}
	}
	// De-select the selected sprite and remove highlights.
	game->refSelectedSprite = NULL;
	UpdateMoveSquares(game);
}

// Return if the button is activated.
int SpriteButtonStateUpdate(ButtonState *bstate, Rectangle boundingBox)
{
	Vector2 mousePos = GetMousePosition();
	int containsMouse = CheckCollisionPointRec(mousePos, boundingBox);
	switch (*bstate)
	{
		case BS_DISABLED:
			// Can't do anything
			break;
		case BS_ENABLED:
			// Check for hover
			if (containsMouse)
			{
				*bstate = BS_HOVER;
			}
			if (*bstate != BS_HOVER)
			{
				break;
			}
			// fall-through
		case BS_HOVER:
			// Check for unhover or press & activation
			if (!containsMouse)
			{
				*bstate = BS_ENABLED;
			}
			else if (IsMouseButtonPressed(0))
			{
				*bstate = BS_PRESSED;
			}
			if (*bstate != BS_PRESSED)
			{
				break;
			}
			// fall-through
		case BS_PRESSED:
			// Check for activation
			if (!containsMouse)
			{
				*bstate = BS_ENABLED;
			}
			else if (IsMouseButtonReleased(0))
			{
				// Newly Activated!
				*bstate = BS_ACTIVATED;
				return 1;
			}
			break;
		case BS_ACTIVATED:
			// No need to do anything
			break;
		default:
			assert(0 && "invalid ButtonState");
	}
	return 0;
}

// Return value: whether the sprite button was just activated this time.
int SpriteButtonUpdate(Sprite *s)
{
	assert(s);
	switch (s->data.kind)
	{
		case SK_PROMOTE_BUTTON:
			return SpriteButtonStateUpdate(&s->data.as_promoteButton.state, s->boundingBox);
		case SK_GENERIC_BUTTON:
			return SpriteButtonStateUpdate(&s->data.as_genericButton.state, s->boundingBox);
		default:
			return 0;
	}
}

// Returns non-zero if the play state has ended early.
int UpdatePlayButtons(GameContext *game)
{
	for (int i = 0; i < arrlen(game->arrUISprites); i++)
	{
		Sprite *s = &game->arrUISprites[i];
		assert(SpriteIsUI(s));
		int didActivate = SpriteButtonUpdate(s);
		if (didActivate)
		{
			// Quit to main menu
			if (TextIsEqual(s->data.as_genericButton.refText, "Quit"))
			{
				GameSwitchState(game, GS_MAIN_MENU);
				return 1;
			}
		}
	}
	return 0;
}

void UpdatePlay(GameContext *game)
{
	Vector2 mousePos = GetMousePosition();
	// Minimum dist. from tile center for dragging piece sprite:
	const int drag = (game->tileSize/2) * (game->tileSize/2);
	if (UpdatePlayButtons(game))
	{
		return;
	}
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
			if (GameIsPointOnBoard(game, mousePos))
			{
				SpriteMoveToNormalChessPiece(game->refSelectedSprite, game);
				int col, row;
				ScreenToNormalChessPos(mousePos.x, mousePos.y, game->boardOffset.x, game->boardOffset.y,
						game->tileSize, &row, &col);
				Vector2 mouseSquare = (Vector2){ col, row };
				if (Vector2ArrFind(game->arrDraggedPieceMoves, mouseSquare))
				{
					// Released mouse over a valid movement square for the piece.
					// Do the chess game move. Do not increment game turn yet.
					GameDoMoveNormalChess(game, col, row);
					assert(!game->refSelectedSprite);
					assert(!game->arrDraggedPieceMoves);
					GameSwitchState(game, GS_PLAY_ANIMATE);
					return;
				}
			}
			else
			{
				// Dragged piece off board -> reset piece sprite to original pos.
				SpriteMoveToNormalChessPiece(game->refSelectedSprite, game);
				game->refSelectedSprite = NULL;
				UpdateMoveSquares(game);
			}
		}
	}
	else if (IsMouseButtonDown(0))
	{
		if (game->refSelectedSprite)
		{
			// Move the current sprite to the mouse pointer if the sprite has already moved or if
			// the mouse is far enough away.
			int x, y;
			int row = game->refSelectedSprite->data.as_normalChessPiece->row;
			int col = game->refSelectedSprite->data.as_normalChessPiece->col;
			NormalChessPosToScreen(row, col, game->boardOffset.x, game->boardOffset.y, game->tileSize,
					&x, &y);
			Vector2 originalPos = (Vector2){ x + game->tileSize/2, y + game->tileSize/2 };
			Vector2 spritePos = (Vector2)
			{
				game->refSelectedSprite->boundingBox.x + game->refSelectedSprite->boundingBox.width/2,
				game->refSelectedSprite->boundingBox.y + game->refSelectedSprite->boundingBox.height/2,
			};
			if (Vector2DistanceSquared(originalPos, spritePos) > 0
					|| Vector2DistanceSquared(mousePos, originalPos) >= drag)
			{
				SpriteMoveCenter(game->refSelectedSprite, mousePos.x, mousePos.y);
			}
		}
	}
}

// Meant to be called from Update.
void UpdatePlayPromote(GameContext *game)
{
	Vector2 mousePos = GetMousePosition();
	// Update all buttons
	for (int i = 0; i < arrlen(game->arrUISprites); i++)
	{
		SpriteButtonUpdate(&game->arrUISprites[i]);
	}
	for (int i = 0; i < arrlen(game->arrUISprites); i++)
	{
		Sprite *s = &game->arrUISprites[i];
		if (s->data.kind == SK_PROMOTE_BUTTON && s->data.as_promoteButton.state == BS_ACTIVATED)
		{
			// The current button has been clicked on.
			// Promote the pawn with the selection.
			assert(game->refSelectedSprite);
			NormalChessPiece *p = game->refSelectedSprite->data.as_normalChessPiece;
			p->kind = s->data.as_promoteButton.pieceKind;
			game->refSelectedSprite->textureRect = NormalChessKindToTextureRect(p->kind);
			GameSwitchState(game, GS_PLAY);
		}
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
	// Nothing to do.
	if (GetKeyPressed())
	{
		GameSwitchState(game, GS_PLAY);
	}
}

void UpdatePlayAnimate(GameContext *game)
{
	// Check for pawn promotion.
	if (NormalChessGetPawnPromotion(game->normalChess))
	{
		// Do promotion. Coming back from promotion state will increment chess game turn.
		GameSwitchState(game, GS_PLAY_PROMOTE);
		return;
	}
	else
	{
		// TODO animate stuff
		GameSwitchState(game, GS_PLAY);
		return;
	}
}

void UpdateDebug(GameContext *game)
{
	if (IsKeyReleased(KEY_ZERO))
	{
		// [0] -> set debug level to zero
		game->isDebug = 0;
	}
	else if (IsKeyReleased(KEY_EQUAL))
	{
		// [+] -> Increase debug level
		game->isDebug++;
	}
	else if (IsKeyReleased(KEY_MINUS))
	{
		// [-] -> Decrease debug level
		// Don't allow isDebug to go negative.
		if (game->isDebug > 0)
		{
			game->isDebug--;
		}
	}
}

void Update(GameContext *game) {
	_Static_assert(_GS_COUNT == 6, "exhaustive handling of all GameState's");
	switch (game->state)
	{
		case GS_PLAY:
			UpdatePlay(game);
			break;
		case GS_PLAY_ANIMATE:
			UpdatePlayAnimate(game);
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
			assert(0 && "game->state should never have the value of GS_NONE in Update()");
	}
	UpdateDebug(game);
	game->ticks++;
	game->stateTicks++;
}

// Draw a slice of a texture centered in the bounds rectangle.
void DrawTextureRecCentered(Texture2D tex, Rectangle slice, Rectangle bounds)
{
	int x = bounds.x + (bounds.width - slice.width)/2;
	int y = bounds.y + (bounds.height - slice.height)/2;
	DrawTextureRec(tex, slice, (Vector2){ x, y }, WHITE);
}

void DrawTextCentered(const char *text, int centerX, int centerY, int fontSize, Color tint)
{
	Font font = GetFontDefault();
	int spacing = 0;
	Vector2 textSize = MeasureTextEx(font, text, fontSize, spacing);
	int x = centerX - textSize.x / 2;
	int y = centerY - textSize.y / 2;
	DrawText(text, x, y, fontSize, tint);
}

void DrawSprite(const GameContext *game, const Sprite *s)
{
	assert(game);
	assert(s);
	switch (s->data.kind)
	{
		case SK_NORMAL_CHESS_PIECE:
			// Draw normal chess piece sprite.
			DrawTextureRecCentered(*s->refTexture,
					NormalChessKindToTextureRect(s->data.as_normalChessPiece->kind),
					s->boundingBox);
			break;
		case SK_PROMOTE_BUTTON:
			// Draw promotion button sprite.
			{
				Rectangle shrunk = (Rectangle)
				{
					.x = s->boundingBox.x + 1,
					.y = s->boundingBox.y + 1,
					.width = s->boundingBox.width - 2,
					.height = s->boundingBox.height - 2,
				};
				const Color fillColor = LIGHTGRAY;
				Color outlineColor = GRAY;
				if (s->data.as_promoteButton.state == BS_ACTIVATED)
				{
					outlineColor = fillColor;
				}
				else if (s->data.as_promoteButton.state == BS_HOVER)
				{
					outlineColor = GREEN;
				}
				DrawRectangleRec(shrunk, fillColor);
				DrawRectangleLinesEx(shrunk, 2, outlineColor);
				DrawTextureRecCentered(*s->refTexture,
						NormalChessKindToTextureRect(s->data.as_promoteButton.pieceKind),
						s->boundingBox);
				break;
			}
		case SK_GENERIC_BUTTON:
			{
				const Color fillColor = LIGHTGRAY;
				const Color hoverColor = RAYWHITE;
				const Color textColor = GRAY;
				Color outlineColor = GRAY;
				Rectangle shrunk = (Rectangle)
				{
					.x = s->boundingBox.x + 1,
					.y = s->boundingBox.y + 1,
					.width = s->boundingBox.width - 2,
					.height = s->boundingBox.height - 2,
				};
				if (s->data.as_genericButton.state == BS_ACTIVATED)
				{
					outlineColor = fillColor;
				}
				else if (s->data.as_genericButton.state == BS_HOVER)
				{
					outlineColor = hoverColor;
				}
				DrawRectangleRec(shrunk, fillColor);
				DrawTextCentered(s->data.as_genericButton.refText, shrunk.x + shrunk.width/2,
						shrunk.y + shrunk.height/2, 20, textColor);
				DrawRectangleLinesEx(shrunk, 2, outlineColor);
				break;
			}
		case SK_NONE:
			// Dummy sprite. Do nothing.
			break;
		default:
			assert(0 && "unhandled SpriteKind");
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
	const int x0 = game->boardOffset.x;
	const int y0 = game->boardOffset.y;
	const int tileSize = game->tileSize;
	const int trans = 180; // highlight square texture transparency
	DrawTileMapComponent(game->tmapBackground);
	// Draw chess board & tiles
	DrawTileMapComponent(game->tmapBoard);
	// Draw move highlight squares.
	if (game->arrDraggedPieceMoves)
	{
		const Rectangle hiSlice = (Rectangle){ .x = 192, .y = 32, .width = 32, .height = 32 };
		const Color tint = (Color){ 255, 255, 255, trans };
		for (int i = 0; i < arrlen(game->arrDraggedPieceMoves); i++)
		{
			Vector2 pos = game->arrDraggedPieceMoves[i];
			int x, y;
			NormalChessPosToScreen(pos.y, pos.x, x0, y0, tileSize, &x, &y);
			Vector2 pos2 = (Vector2){ x, y };
			DrawTextureRec(game->texBoard, hiSlice, pos2, tint);
		}
	}
	// Draw selected piece highlight square.
	if (game->refSelectedSprite)
	{
		const NormalChessPiece *p = game->refSelectedSprite->data.as_normalChessPiece;
		const Color tint = (Color){ 255, 255, 255, trans };
		if (p)
		{
			int x, y;
			NormalChessPosToScreen(p->row, p->col, x0, y0, tileSize, &x, &y);
			Rectangle selSlice = (Rectangle){ .x = 224, .y = 32, .width = 32, .height = 32 };
			Vector2 pos = (Vector2){ x, y };
			DrawTextureRec(game->texBoard, selSlice, pos, tint);
		}
	}
	// Draw normal chess sprites except for the selected one.
	for (int i = 0; i < arrlen(game->arrSprites); i++)
	{
		Sprite *s = &game->arrSprites[i];
		if (s->data.kind != SK_NORMAL_CHESS_PIECE)
		{
			continue;
		}
		if (!game->refSelectedSprite || game->refSelectedSprite != s)
		{
			DrawSprite(game, s);
		}
	}
	// Draw buttons / menu / GUI
	for (int i = 0; i < arrlen(game->arrUISprites); i++)
	{
		Sprite *s = &game->arrUISprites[i];
		assert(SpriteIsUI(s));
		DrawSprite(game, s);
	}
	// Draw the selected sprite piece now so it is always on top.
	if (game->refSelectedSprite)
	{
		DrawSprite(game, game->refSelectedSprite);
	}
}

void DrawGameOver(const GameContext *game)
{
	DrawPlay(game);
	DrawText("Game over", 20, 50, 16, RED);
}

void DrawMainMenu(const GameContext *game)
{
	ClearBackground(RAYWHITE);
	// Draw menu title.
	Texture2D texture = game->texGUI;
	Rectangle slice = (Rectangle){ 0, 0, 160, 64 };
	Rectangle dest = (Rectangle){ 150, 80, slice.width*2, slice.height*2 };
	Vector2 origin = (Vector2){ 0, 0 };
	float rotation = 0;
	float scale = 2;
	Color tint = WHITE;
	DrawTexturePro(texture, slice, dest, origin, rotation, tint);
}

// Draw additional debug info regardless of what the game state is.
// Game-state specific code should be in the state's own draw function.
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
		DrawText(TextFormat("state ticks: %d", game->stateTicks), 10, 56, 20, GREEN);
	}
}

void DrawPlayAnimate(const GameContext *game)
{
	// TODO: implement
}

void DrawPlayPromote(const GameContext *game)
{
	const int arrowGap = 10;
	const int arrowSize = 20;
	const int textGapX = 7;
	const int textGapY = 5;
	assert(game);
	// Use play state drawing.
	DrawPlay(game);
	assert(game->refSelectedSprite);
	// Draw the menu for selecting a piece rank to promote to.
	int startX = game->refSelectedSprite->boundingBox.x + game->refSelectedSprite->boundingBox.width/2;
	int startY = game->refSelectedSprite->boundingBox.y + game->refSelectedSprite->boundingBox.height/2;
	int lineY1;
	if (NormalChessCurrentKing(game->normalChess) == WHITE_KING)
	{
		lineY1 = game->promotionMenuRect.y + arrowGap;
	}
	else
	{
		lineY1 = game->promotionMenuRect.y + game->promotionMenuRect.height - arrowGap - arrowSize;
	}
	int lineY2 = lineY1 + arrowSize;
	int lineEndX;
	if (game->promotionMenuRect.x > startX)
	{
		startX += game->tileSize / 4;
		lineEndX = game->promotionMenuRect.x;
		DrawTriangle((Vector2){ startX, startY },
				(Vector2){ lineEndX, lineY2 },
				(Vector2){ lineEndX, lineY1 }, 
				RAYWHITE);
	}
	else
	{
		startX -= game->tileSize / 4;
		lineEndX = game->promotionMenuRect.x + game->promotionMenuRect.width;
		DrawTriangle((Vector2){ startX, startY },
				(Vector2){ lineEndX, lineY1 }, 
				(Vector2){ lineEndX, lineY2 },
				(Color){ 255, 255, 255, 100 });
	}
	float roundness = 0.08;
	float numSegments = 3;
	DrawRectangleRounded(game->promotionMenuRect, roundness, numSegments, RAYWHITE);
	DrawText("Pawn Promotion", game->promotionMenuRect.x + textGapX, game->promotionMenuRect.y + textGapY,
			20, BLUE);
	// Draw button sprites.
	for (int i = 0; i < arrlen(game->arrUISprites); i++)
	{
		Sprite *s = &game->arrUISprites[i];
		if (s->data.kind == SK_PROMOTE_BUTTON)
		{
			DrawSprite(game, s);
		}
	}
}

void Draw(const GameContext *game) {
	_Static_assert(_GS_COUNT == 6, "exhaustive handling of all GameState's");
	switch (game->state)
	{
		case GS_PLAY:
			DrawPlay(game);
			break;
		case GS_PLAY_ANIMATE:
			DrawPlayAnimate(game);
			break;
		case GS_PLAY_PROMOTE:
			DrawPlayPromote(game);
			break;
		case GS_GAME_OVER:
			DrawGameOver(game);
			break;
		case GS_MAIN_MENU:
			DrawMainMenu(game);
			break;
		case GS_NONE:
			assert(0 && "unhandled state");
			break;
	}
	DrawDebug(game);
}

// Reset the game's current state.
// Note: not guaranteed for the game state to have it's variables correctly set up because some
// things must be set by the previous state, e.g: GS_PLAY_PROMOTE needs to be correctly set up by
// GS_PLAY. 
void GameResetState(GameContext *game)
{
	assert(game);
	assert(game->state != GS_NONE);
	GameLeaveState(game, GS_NONE);
	GameEnterState(game, GS_NONE);
}

void GameCleanup(GameContext *game)
{
	GameCleanupState(game);
	// Make sure every pointer has been dealt with
	assert(game->normalChess == NULL);
	assert(game->arrDraggedPieceMoves == NULL);
	assert(game->arrSprites == NULL);
	assert(game->arrUISprites == NULL);
	assert(game->refSelectedSprite == NULL);
	assert(game->tmapBoard == NULL);
	assert(game->tmapBackground == NULL);
	// TODO: cleanup textures?
}

void Test(void)
{
	TestNormalChessMovesContains();
}

/* vi: set colorcolumn=101 textwidth=100 tabstop=4 noexpandtab: */
