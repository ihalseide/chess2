#ifndef __GAME_H
#define __GAME_H

#include "raylib.h"
#include "tilemap.h"
#include <assert.h>

typedef enum GameState
{
	GS_NONE,         // The game should never be in this state, but it is used at the beginning.
	GS_PLAY,         // This state is the main play state.
	GS_PLAY_ANIMATE, // Sub-state of play state
	GS_PLAY_PROMOTE, // Sub-state of play state
	GS_GAME_OVER,    // Sub-state of play state
	GS_MAIN_MENU,
} GameState;
#define _GS_COUNT (GS_MAIN_MENU + 1)
_Static_assert(_GS_COUNT == 6, "exhaustive handling of all GameState's");

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
	SK_GENERIC_BUTTON,
	SK_PROMOTE_BUTTON,
	SK_NORMAL_CHESS_PIECE,
} SpriteKind;

typedef struct NormalChessPiece
{
	NormalChessKind kind;
	int col; // position column
	int row; // position row
} NormalChessPiece;

typedef struct NormalChessMove 
{
	int subjectCol; // The subject is the piece moving or capturing. The subject moves from this location.
	int subjectRow;
	int objectCol;  // The object is the other piece which is being captured (or is the rook when castling)
	int objectRow;
	int targetCol;  // The square the subject piece is moving to.
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

typedef enum ButtonState
{
	BS_DISABLED,  // unable to be used
	BS_ENABLED,   // able to be used, but not currently in any other state
	BS_HOVER,     // button is being hovered over
	BS_PRESSED,   // button was clicked on, but not released (yet)
	BS_ACTIVATED, // button was clicked on and released on and is activated
} ButtonState;

typedef struct PiecePromoteButton
{
	ButtonState state;
	NormalChessKind pieceKind;
} PiecePromoteButton;

typedef struct GenericButton
{
	ButtonState state;
	const char *refText;  // text to draw on top (if any)
} GenericButton;

// Tagged union for the data of different kinds of sprites.
// Note: don't give a sprite any "owned" pointers to memory, because it might
// not be free'd when the sprite is.
typedef struct SpriteData
{
	SpriteKind kind;
	union {
		NormalChessPiece *as_normalChessPiece; // for normal chess game pieces.
		PiecePromoteButton as_promoteButton;
		GenericButton as_genericButton;
	};
} SpriteData;

// Note: don't give a sprite any "owned" pointers to memory, because it might
// not be free'd when the sprite is.
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
	GameState state;  // see the note above this struct definition.
	Texture2D texPieces;  // spritesheet textures for pieces
	Texture2D texBoard;  // spritesheet textures for board and background
	Texture2D texGUI;  // spritesheet textures for user interface specific stuff
	Sound soundCapture;
	Sound soundMove;
	Sound soundPromote;
	Sound soundEnterPromote;
	Sound soundCheck;
	Sound soundCheckmate;
	Sound soundCastle;
	Sound soundError;
	Sound soundGameOver;
	Sound soundGameStart;
	Sound soundResign;
	Vector2 boardOffset;  // pixels
	Rectangle promotionMenuRect;
	int isDebug;  // higher number generally means more info
	int ticks;  // ticks since the program started
	int stateTicks; // ticks since the current state was entered
	int tileSize;
	NormalChess *normalChess;
	Vector2 *arrDraggedPieceMoves;  // board coordinates (col, row)
	Sprite *arrSprites;  // dynamic array of game sprites
	Sprite *arrUISprites;  // dynamic array of user interface Sprites
	Sprite *refSelectedSprite;
	TileMapComponent *tmapBoard;
	TileMapComponent *tmapBackground;
} GameContext;

NormalChess *NormalChessAlloc(int turn, NormalChessPiece **arrPieces);
NormalChess *NormalChessInit(void);
NormalChessKind NormalChessCurrentKing(const NormalChess *chess);
NormalChessKind NormalChessEnemyKingKind(NormalChessKind k);
NormalChessKind NormalChessKingKind(NormalChessKind k);
NormalChessKind PieceKingOf(const NormalChessPiece *p);
NormalChessMove NormalChessCreateCastleMove(NormalChess *chess, NormalChessPiece *p, int targetCol);
NormalChessMove NormalChessCreateMove(NormalChess *chess, int startCol, int startRow, int targetCol,
		int targetRow);
NormalChessMove NormalChessCreatePawnMove(NormalChess *chess, NormalChessPiece *p, int targetCol,
		int targetRow);
NormalChessPiece *GameGetPieceAt(const GameContext *game, Vector2 screenPos);
NormalChessPiece *GameGetValidSelectedPiece(const GameContext *game);
NormalChessPiece *NormalChessGetPawnPromotion(NormalChess *chess);
NormalChessPiece *NormalChessMoveGetObject(NormalChessMove move, NormalChessPiece **arrPieces);
NormalChessPiece *NormalChessMoveGetObjectInfo(NormalChess *chess, NormalChessMove move,
		NormalChessPiece **object, int *isCapture, int *isCastle);
NormalChessPiece *NormalChessMoveGetSubject(NormalChessMove move, NormalChessPiece **arrPieces);
NormalChessPiece *NormalChessPieceAlloc(NormalChessKind k, int row, int col);
NormalChessPiece *PiecesGetAt(NormalChessPiece **arrPieces, int row, int col);
Rectangle GameGetBoardRect(const GameContext *game);
Rectangle NormalChessKindToTextureRect(NormalChessKind k);
Sprite *SpritesArrCreateNormalChess(GameContext *game);
Sprite *SpritesArrFindNormalChessSpriteAt(Sprite *arrSprites, int col, int row);
Sprite *SpritesArrFindNormalChessSpriteFor(Sprite *arrSprites, NormalChessPiece *forPiece);
Sprite *SpritesArrFindSpriteAt(Sprite *arrSprites, int x, int y);
Vector2 *NormalChessCreatePieceMoveList(const NormalChess *c, NormalChessPiece *p);
Vector2 *Vector2ArrFind(Vector2 *arrVectors, Vector2 val);
const NormalChessPiece *PiecesFindKing(const NormalChessPiece **arrPieces, NormalChessKind k);
const NormalChessPiece *PiecesGetAtConst(const NormalChessPiece **arrPieces, int row, int col);
const char *GameStateToStr(GameState s);
const char *NormalChessKindToStr(NormalChessKind k);
const char *SpriteKindToStr(SpriteKind k);
float Vector2DistanceSquared(Vector2 a, Vector2 b);
int GameIsPointOnBoard(const GameContext *game, Vector2 screenPos);
int NormalChessAllMovesContains(const NormalChess *c, NormalChessPiece *p, int row, int col);
int NormalChessCanMove(NormalChess *chess);
int NormalChessCanUsePiece(const NormalChess *chess, const NormalChessPiece *p);
int NormalChessIsCheckmate(NormalChess *chess);
int NormalChessIsGameOver(NormalChess *chess);
int NormalChessIsKingInCheck(NormalChess *chess);
int NormalChessIsStalemate(NormalChess *chess);
int NormalChessMovesContains(const NormalChessPiece *p, int row, int col);
int NormalChessPieceTeamEq(const NormalChessPiece *a, const NormalChessPiece *b);
int NormalChessSpecialMovesContains(const NormalChess *chess, const NormalChessPiece *p, int row, int col);
int NormalChessTeamEq(NormalChessKind a, NormalChessKind b);
int PiecesCanTeamCaptureSpot(const NormalChessPiece **arrPieces, NormalChessKind team, int targetRow,
		int targetCol);
int PiecesCountAtConst(const NormalChessPiece **arrPieces, int row, int col);
int PiecesIsPiecePinned(const NormalChessPiece **arrPieces, NormalChessPiece *p, int targetRow,
		int targetCol);
int PiecesMoveIsBlocked(const NormalChessPiece **arrPieces, const NormalChessPiece *p, int targetRow,
		int targetCol);
int SpriteButtonStateUpdate(ButtonState *bstate, Rectangle boundingBox);
int SpriteButtonUpdate(Sprite *s);
int SpriteIsUI(Sprite *s);
int SpriteKindIsUI(SpriteKind k);
int UpdatePlayButtons(GameContext *game);
void ClearMoveSquares(GameContext *game);
void Draw(const GameContext *game);
void DrawDebug(const GameContext *game);
void DrawGameOver(const GameContext *game);
void DrawMainMenu(const GameContext *game);
void DrawPlay(const GameContext *game);
void DrawPlayAnimate(const GameContext *game);
void DrawPlayPromote(const GameContext *game);
void DrawSprite(const GameContext *game, const Sprite *s);
void DrawTextCentered(const char *text, int centerX, int centerY, int fontSize, Color tint);
void DrawTextureRecCentered(Texture2D tex, Rectangle slice, Rectangle bounds);
void GameCleanup(GameContext *game);
void GameCleanupState(GameContext *game);
void GameDoMoveNormalChess(GameContext *game, int targetCol, int targetRow);
void GameEnterState(GameContext *game, GameState previous);
void GameEnterStateGameOver(GameContext *game, GameState previous);
void GameEnterStateMainMenu(GameContext *game, GameState previous);
void GameEnterStatePlay(GameContext *game, GameState previous);
void GameEnterStatePlayAnimate(GameContext *game, GameState previous);
void GameEnterStatePlayPromote(GameContext *game, GameState previous);
void GameLeaveState(GameContext *game, GameState next);
void GameLeaveStateGameOver(GameContext *game, GameState next);
void GameLeaveStateMainMenu(GameContext *game, GameState next);
void GameLeaveStatePlay(GameContext *game, GameState next);
void GameLeaveStatePlayAnimate(GameContext *game, GameState next);
void GameLeaveStatePlayPromote(GameContext *game, GameState next);
void GameResetState(GameContext *game);
void GameSwitchState(GameContext *game, GameState newState);
void IntClamp(int *value, int min, int max);
void NormalChessDestroy(NormalChess *p);
void NormalChessDoCastle(NormalChess *chess, NormalChessMove move);
void NormalChessDoMove(NormalChess *chess, NormalChessMove move);
void NormalChessDoPawnSpecial(NormalChess *chess, NormalChessMove move);
void NormalChessFree(NormalChess *p);
void NormalChessPieceFree(NormalChessPiece *p);
void NormalChessPosToScreen(int row, int col, int x0, int y0, int tileSize, int *x, int *y);
void NormalChessUpdateMovementFlags(NormalChess *chess, NormalChessMove move);
void PiecesDoCapture(NormalChessPiece **arrPieces, int startRow, int startCol, int targetRow,
		int targetCol);
void PiecesDoMove(NormalChessPiece **arrPieces, int startRow, int startCol, int targetRow, int targetCol);
void PiecesRemovePieceAt(NormalChessPiece **arrPieces, int row, int col);
void PlayInitBackgroundTiles(GameContext *game);
void PlayInitBoardTiles(GameContext *game);
void ScreenSnapCoords(int pX, int pY, int x0, int y0, int tileSize, int *pX2, int *pY2);
void ScreenToNormalChessPos(int pX, int pY, int x0, int y0, int tileSize, int *row, int *col);
void ScreenToTile(int pX, int pY, int x0, int y0, int tileSize, int *tX, int *tY);
void SpriteMoveCenter(Sprite *s, int centerX, int centerY);
void SpriteMoveToNormalChessPiece(Sprite *s, const GameContext *game);
void SpriteSetAsNormalChessPiece(Sprite *s, NormalChessPiece *p);
void SpritesArrRemoveSprite(Sprite **refArrSprites, Sprite *removeMe);
void Test(void);
void TestNormalChessMovesContains(void);
void TileToScreen(int tX, int tY, int x0, int y0, int tileSize, int *pX, int *pY);
void Update(GameContext *game);
void UpdateDebug(GameContext *game);
void UpdateGameOver(GameContext *game);
void UpdateMainMenu(GameContext *game);
void UpdateMoveSquares(GameContext *game);
void UpdatePlay(GameContext *game);
void UpdatePlayAnimate(GameContext *game);
void UpdatePlayPromote(GameContext *game);

#endif /* __GAME_H */
