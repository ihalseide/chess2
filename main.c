#define STB_DS_IMPLEMENTATION
#include "stb_ds.h"
#include "raylib.h"
#include "game.h"

int main(void) {
	Test();
	// Init:
	const int screenWidth = 600;
	const int screenHeight = 480;
	InitWindow(screenWidth, screenHeight, "Chess 2");
	InitAudioDevice();
	SetTargetFPS(30);
	GameContext game = (GameContext)
	{
		.isDebug              = 0, // int for game debug value, higher number means more debug info
		.ticks                = 0,
		.stateTicks           = 0,
		.normalChess          = NULL,
		.arrDraggedPieceMoves = NULL,
		.refSelectedSprite    = NULL,
		.arrSprites           = NULL,
		.arrUISprites         = NULL,
		.tmapBoard            = NULL,
		.tmapBackground       = NULL,
		.state                = GS_PLAY, // initial state
		.tileSize             = 32,
		.texPieces            = LoadTexture("gfx/pieces.png"),
		.texBoard             = LoadTexture("gfx/board.png"),
		.texGUI               = LoadTexture("gfx/gui.png"),
		.soundCapture         = LoadSound("sfx/capture.wav"),
		.soundMove            = LoadSound("sfx/move.wav"),
		.soundEnterPromote    = LoadSound("sfx/can promote.wav"),
		.soundPromote         = LoadSound("sfx/promote.wav"),
		.soundCheck           = LoadSound("sfx/check.wav"),
		.soundCheckmate       = LoadSound("sfx/checkmate.wav"),
		.soundCastle          = LoadSound("sfx/castle.wav"),
		.soundError           = LoadSound("sfx/error.wav"),
		.soundGameOver        = LoadSound("sfx/game over.wav"),
		.soundResign          = LoadSound("sfx/resign.wav"),
		.soundGameStart       = LoadSound("sfx/game start.wav"),
	};
	// Begin
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
	CloseAudioDevice();
	CloseWindow();
	return 0;
}

/* vi: set colorcolumn=101 textwidth=100 tabstop=4 noexpandtab: */
