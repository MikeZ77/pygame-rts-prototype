import time
from typing import List, Tuple

import numpy as np
import pygame as pg
from pygame import Rect, Surface
from pygame.math import Vector2
from pygame.sprite import Sprite

from constants import BLACK, NEON_GREEN, TILE_HEIGHT, TILE_WIDTH, YELLOW
from search import a_star_search
from types_ import TileType


class Tile(Sprite):
    """
    A tile is a Rect which is the foundation for the tile map.

    Args:
        tile_type: What kind of object the tile is (passable or non-passable)
        x: The x coordinate pixel
        y: The y coordinate pixel
        width: The width of the tile map
        height: The height of the tile map
    """

    def __init__(self, tile_type: TileType, x: int, y: int):
        super().__init__()
        self.type = tile_type
        self.rect = Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
        self.is_path = False


class Map:
    """
    This is a temporary sample map that can be used just to get
    some of the pathfinding logic down.

    Args: None
    """

    def __init__(self, map_surface: Surface):
        self.map_surface = map_surface
        self.grid = False
        self.path: List[Tile] = []
        self.holes: List[Tile] = []
        self.cols = self.map_surface.get_width() // TILE_WIDTH  # x
        self.rows = self.map_surface.get_height() // TILE_HEIGHT  # y
        self._map: List[List[Tile]] = []
        self._simple_map = np.empty((self.cols, self.rows), dtype=np.int32)

        for col in range(self.cols):
            self._map.append([])
            for row in range(self.rows):
                self._simple_map[col][row] = TileType.PASSABLE.value
                self._map[col].append(Tile(TileType.PASSABLE, col * TILE_WIDTH, row * TILE_HEIGHT))
        print(self.map_surface.get_width(), self.map_surface.get_height())
        print(self._simple_map.shape)

    def __repr__(self) -> str:
        map_outline = ""
        for col in range(self.cols):
            for row in range(self.rows):
                tile = self._map[col][row]
                if tile.prev:
                    map_outline += "x"
                else:
                    map_outline += str(tile.type.value)
            map_outline += "\n"
        return map_outline

    def _get_tile(self, pixel_pos: Tuple[int, int], coord=False) -> Tile:
        """
        Takes the x,y vector pixel coordinates and returns the tile at that postion.
        """
        x = int(pixel_pos.x // TILE_WIDTH)
        y = int(pixel_pos.y // TILE_HEIGHT)

        if coord:
            return x, y
        return self._map[x][y]

    def draw(self, display_surface: Surface, camera_rect: Rect):
        # self.map_surface.fill(GREEN)
        for tile in self.path:
            if tile.is_path:
                pg.draw.rect(display_surface, YELLOW, tile)

        for tile in self.holes:
            pg.draw.rect(display_surface, BLACK, tile)

        if self.grid:
            top = abs(camera_rect.top) // TILE_WIDTH
            left = abs(camera_rect.left) // TILE_HEIGHT
            cols = camera_rect.width // TILE_WIDTH
            rows = camera_rect.height // TILE_HEIGHT
            for x in range(top, cols):
                for y in range(left, rows):
                    tile = self._map[x][y]
                    pg.draw.rect(display_surface, NEON_GREEN, tile, 1)

    def add_hole(self, pos: Vector2):
        tile = self._get_tile(pos)
        tile.type = TileType.NOT_PASSABLE
        self.holes.append(tile)
        # For the simple grid
        x = int(pos.x // TILE_WIDTH)
        y = int(pos.y // TILE_HEIGHT)
        self._simple_map[x][y] = TileType.NOT_PASSABLE.value

    def find_path(self, start, goal):
        start = self._get_tile(start, coord=True)
        goal = self._get_tile(goal, coord=True)
        print(goal)
        grid = self._simple_map
        path = a_star_search(start, goal, grid)
        self.path = []
        for x, y in path:
            tile = self._map[x][y]
            tile.is_path = True
            self.path.append(tile)
        return self.path


# if __name__ == "__main__":
#     from main import main

#     main()
# grid = np.zeros((2000, 2000), dtype=int)
# start_time = time.perf_counter()
# path = a_star_search((0, 0), (1951, 1111), grid)
# print(time.perf_counter() - start_time, "\n")
# print(1 / 60)
# print(path)

# map = Map()
# start_pos = Vector2(0, 0)
# end_pos = Vector2(100, 180)
# start_time = time.perf_counter()
# path = map.find_path(start_pos, end_pos)
# print(map)
# print(time.perf_counter() - start_time, "\n")
# print("Goal=", 100 // TILE_WIDTH, 180 // TILE_HEIGHT)
# print(len(path))
# for tile in path:
#     print(tile.x, tile.y)
