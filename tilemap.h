#ifndef _TILE_MAP_H
#define _TILE_MAP_H

#include "raylib.h"

typedef struct TileMap
{
	int rows;
	int columns;
	int *arrTileIDs; // array of tile IDs (not a dynamic array)
} TileMap;

typedef struct TileInfo
{
	int x0; // (x0, y0) is the corner of tile's region in texture (size is stored in the TileMapComponent)
	int y0;
	Texture2D *refTexture; // reference to texture
} TileInfo;

typedef struct TileMapComponent
{
	int x0;
	int y0;
	int tileSize;
	TileInfo *arrTileInfo; // dynamic array of TileInfo's, indexed by tile IDs, (owns this pointer)
	TileMap *map; // (owns this pointer)
} TileMapComponent;

TileMap *TileMapAlloc(int columns, int rows);
TileMapComponent *TileMapComponentAlloc(int x0, int y0, int tileSize, int columns, int rows);
int *TileMapGet(TileMap *map, int col, int row);
void TileMapComponentFree(TileMapComponent *p);
void TileMapFree(TileMap *p);
void DrawTileMapComponent(TileMapComponent *tmap);
void TileMapComponentSet(TileMapComponent *tmap, int col, int row, TileInfo tile);

#endif /* _TILE_MAP_H */
