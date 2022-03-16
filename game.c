#include <stdio.h>
#include <assert.h>
#include <raylib.h>

typedef enum GameState {
} GameState;

Texture2D spritesheet;

GameState theState;

void update () {

}

void drawSprite (int x, int y, int sheetX, int sheetY) {
	// Get the sprite at sheetX, sheetY
	// draw it
}

void draw () {
    ClearBackground(RAYWHITE);
    DrawTexture(spritesheet, 0, 0, WHITE);
}

void init () {
    const int screenWidth = 600;
    const int screenHeight = 480;

    InitWindow(screenWidth, screenHeight, "Chezz");
    SetTargetFPS(30);

    spritesheet = LoadTexture("textures.png");
}

void loop () {
    while (!WindowShouldClose()) {
        update();

        BeginDrawing();
        draw();
        EndDrawing();
    }
}

void end () {
    CloseWindow();
}

int main (void) {
    init();
    loop();
    end();
    return 0;
}
