#include <assert.h>
#include <stdlib.h>
#include "stb_ds.h"
#include "tilemap.h"

// Allocate new tile map.
// Tile IDs are initially set to 0.
// Must be freed with TileMapFree
TileMap *TileMapAlloc(int columns, int rows)
{
	TileMap *new = malloc(sizeof(*new));
	if (new)
	{
		new->columns = columns;
		new->rows = rows;
		int size = columns * rows;
		new->arrTileIDs = malloc(sizeof(*new->arrTileIDs) * size);
		if (new->arrTileIDs)
		{
			for (int i = 0; i < size; i++)
			{
				new->arrTileIDs[i] = 0;
			}
		}
	}
	return new;
}

void TileMapFree(TileMap *p)
{
	free(p);
}

// Allocates a new TileMapComponent.
// Must be free'd with TileMapComponentFree when done.
TileMapComponent *TileMapComponentAlloc(int x0, int y0, int tileSize, int columns, int rows)
{
	TileMapComponent *new = malloc(sizeof(*new));
	if (new)
	{
		new->x0 = x0;
		new->y0 = y0;
		new->tileSize = tileSize;
		new->arrTileInfo = NULL; // empty dynamic array
		new->map = TileMapAlloc(columns, rows);

		// Set the first tile to empty
		arrput(new->arrTileInfo, (TileInfo){0});
	}
	return new;
}

void TileMapComponentFree(TileMapComponent *p)
{
	TileMapFree(p->map);
	arrfree(p->arrTileInfo);
	free(p);
}

// Return pointer to tile ID location in tilemap.
int *TileMapGet(TileMap *map, int col, int row)
{
	if (0 <= col && col < map->columns && 0 <= row && row < map->rows)
	{
		int i = (row * map->columns) + col;
		return &map->arrTileIDs[i];
	}
	else
	{
		return NULL;
	}
}

void DrawTileMapComponent(TileMapComponent *tmap)
{
	if (!tmap)
	{
		return;
	}
	assert(tmap->map);
	for (int r = 0; r < tmap->map->rows; r++)
	{
		int y = tmap->y0 + r * tmap->tileSize;
		for (int c = 0; c < tmap->map->columns; c++)
		{
			int x = tmap->x0 + c * tmap->tileSize;
			int id = *TileMapGet(tmap->map, c, r);
			if (id > 0 && id < arrlen(tmap->arrTileInfo))
			{
				TileInfo t = tmap->arrTileInfo[id];
				const Color tint = WHITE;
				const Vector2 pos = (Vector2){ x, y };
				const Rectangle src = (Rectangle){ t.x0, t.y0, tmap->tileSize, tmap->tileSize };
				DrawTextureRec(*t.refTexture, src, pos, tint); 
			}
		}
	}
	// Debug draw:
	//const int width = tmap->tileSize * tmap->map->columns;
	//const int height = tmap->tileSize * tmap->map->rows;
	//DrawRectangleLines(tmap->x0, tmap->y0, width, height, RED);
}

static int TileInfoArrFind(const TileInfo *arrTileInfo, TileInfo t)
{
	for (int i = 0; i < arrlen(arrTileInfo); i++)
	{
		TileInfo item = arrTileInfo[i];
		if (item.refTexture == t.refTexture && item.x0 == t.x0 && item.y0 == t.y0)
		{
			return i;
		}
	}
	return -1;
}

// May grow the TileMapComponent's arrTileInfo dynamic array.
// Returns the tile id that was chosen.
int TileMapComponentSet(TileMapComponent *tmap, int col, int row, TileInfo tile)
{
	if (0 <= col && col < tmap->map->columns && 0 <= row && row < tmap->map->rows)
	{
		int id = TileInfoArrFind(tmap->arrTileInfo, tile);
		if (id < 0)
		{
			// Not a previously existing TileInfo, so add it.
			id = arrlen(tmap->arrTileInfo);
			arrput(tmap->arrTileInfo, tile);
		}
		int *loc = TileMapGet(tmap->map, col, row);
		if (loc)
		{
			*loc = id;
		}
		return id;
	}
	return -1;
}

