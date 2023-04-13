# from random import random, seed
import heapq
import time
from typing import List, Tuple

import pygame as pg
from pygame import Rect, Surface
from pygame.math import Vector2

# from pygame.math import Vector2
from pygame.sprite import Sprite

from constants import BLACK, GREEN, NEON_GREEN, TILE_HEIGHT, TILE_WIDTH, YELLOW
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

    def __init__(self, tile_type: TileType, x: int, y: int, width: int, height: int):
        super().__init__()
        self.type = tile_type
        self.rect = Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
        # TODO: We want each tile to know its neighbour on the grid, so we need its x, y coord
        # on the grid and the total rows and columns
        self.x = x // TILE_WIDTH
        self.y = y // TILE_HEIGHT
        self.width = width
        self.height = height
        # f = g + h
        self.f = 0
        self.g = 0
        self.h = 0
        self.is_path = False
        self.prev: Tile = None
        self.adj_coords: list[Tuple[int, int]] = []
        self._get_adj_coords()

    def __eq__(self, other) -> bool:
        if isinstance(other, Tile):
            return self.x == other.x and self.y == other.y

    def __lt__(self, other) -> bool:
        if isinstance(other, Tile):
            return self.f < other.f

    def _get_adj_coords(self):
        # TODO: This is only adjacent if it is type PASSABLE
        # Check the left neighbour
        if self.x > 0:
            self.adj_coords.append((self.x - 1, self.y))

        # Check the right neighbour
        if self.x < self.width - 1:
            self.adj_coords.append((self.x + 1, self.y))

        # Check the top neighbour
        if self.y > 0:
            self.adj_coords.append((self.x, self.y - 1))

        # Check the bottom neighbour
        if self.y < self.height - 1:
            self.adj_coords.append((self.x, self.y + 1))

        # Check the diagonal up-right neighbour
        if self.x < self.width and self.y > 0:
            self.adj_coords.append((self.x + 1, self.y - 1))

        # Check the diagonoal up-left neighour
        if self.x > 0 and self.y > 0:
            self.adj_coords.append((self.x - 1, self.y - 1))

        # Check the diagonal bottom-left neighbour
        if self.x > 0 and self.y < self.height - 1:
            self.adj_coords.append((self.x - 1, self.y + 1))

        # Check the diagonal bottom-right neighbour
        if self.x < self.width - 1 and self.y < self.height - 1:
            self.adj_coords.append((self.x + 1, self.y + 1))

    def set_type(self, map: "Map", tile_type: TileType):
        self.type = tile_type
        if tile_type == TileType.NOT_PASSABLE:
            for coord in self.adj_coords:
                x, y = coord
                tile: Tile = map._map[x][y]
                tile.adj_coords[:] = [
                    coord_ for coord_ in tile.adj_coords if coord_ != (self.x, self.y)
                ]


class Map:
    """
    This is a temporary sample map that can be used just to get
    some of the pathfinding logic down.

    Args: None
    """

    def __init__(self, map_surface: Surface):
        self.map_surface = map_surface
        self._map: List[List[Tile]] = []
        self.grid = False
        self.path: List[Tile] = []
        self.holes: List[Tile] = []
        self.cols = self.map_surface.get_width() // TILE_WIDTH
        self.rows = self.map_surface.get_height() // TILE_HEIGHT

        print(self.map_surface.get_width(), self.map_surface.get_height())

        for col in range(self.cols):
            self._map.append([])
            for row in range(self.rows):
                self._map[col].append(
                    Tile(
                        TileType.PASSABLE, col * TILE_WIDTH, row * TILE_HEIGHT, self.cols, self.rows
                    )
                )

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

    def _get_tile(self, pixel_pos: Vector2) -> Tile:
        """
        Takes the x,y vector pixel coordinates and returns the tile at that postion.
        """
        x = int(pixel_pos.x // TILE_WIDTH)
        y = int(pixel_pos.y // TILE_HEIGHT)
        return self._map[x][y]

    def draw(self, display_surface: Surface):
        # self.map_surface.fill(GREEN)
        for tile in self.path:
            if tile.is_path:
                pg.draw.rect(display_surface, YELLOW, tile)

        for tile in self.holes:
            pg.draw.rect(display_surface, BLACK, tile)

        # TODO: The grid should only be rendered over the current view port
        #         if self.grid:
        #             pg.draw.rect(display_surface, NEON_GREEN, tile, 1)

        # for col in range(self.cols):
        #     for row in range(self.rows):
        #         tile = self._map[col][row]

        #         if tile.type == TileType.PASSABLE:
        #             pg.draw.rect(display_surface, YELLOW, tile) if tile.is_path else pg.draw.rect(
        #                 display_surface, GREEN, tile
        #             )

        #         # if tile.type == TileType.PASSABLE and tile.is_path:
        #         #     pg.draw.rect(display_surface, YELLOW, tile)

        #         if tile.type == TileType.NOT_PASSABLE:
        #             pg.draw.rect(display_surface, BLACK, tile)

        #         if self.grid:
        #             pg.draw.rect(display_surface, NEON_GREEN, tile, 1)

    def add_hole(self, pos: Vector2):
        tile = self._get_tile(pos)
        tile.set_type(self, TileType.NOT_PASSABLE)
        self.holes.append(tile)

    def find_path(self, start_pos: Vector2, end_pos: Vector2) -> List[Vector2]:
        start_tile = self._get_tile(start_pos)
        end_tile = self._get_tile(end_pos)
        searched_cells = 0

        open_set = []  # Nodes that need to be evaluated
        heapq.heappush(open_set, (start_tile.f, start_tile))
        closed_set: List[Tile] = []

        # Finised when open_set is empty
        while len(open_set):
            # current should be the node in the open set that has the lowest f score
            # TODO: only add tiles that are type PASSABLE
            current: Tile
            _, current = heapq.heappop(open_set)
            closed_set.append(current)

            if current == end_tile:
                # Backtrack to get the path
                print("Done")
                print("searched cells: ", searched_cells)
                path = [end_tile]
                temp = current
                path.append(temp)
                while temp.prev:
                    temp.is_path = True
                    path.append(temp.prev)
                    temp = temp.prev
                # TODO: Store these node properties in a seperate data structure so we dont have
                # to come back and reset.
                for col in range(self.cols):
                    for row in range(self.rows):
                        tile = self._map[col][row]
                        tile.prev = None
                        tile.f = 0
                        tile.g = 0
                        tile.h = 0

                # TODO: Remove this shared object: just for visualization right now
                self.path = path[0:-1]
                return self.path

            # Get neighbours
            for x, y in current.adj_coords:
                searched_cells += 1
                neighbour = self._map[x][y]

                if neighbour not in closed_set:
                    temp_g = current.g + 1
                    temp_h = (
                        temp_g
                        + (Vector2(end_tile.rect.center) - Vector2(neighbour.rect.center)).length()
                    )
                    if neighbour in open_set:
                        index = open_set.index(neighbour)
                        if open_set[index].f < temp_h:
                            continue

                    if neighbour in closed_set:
                        index = closed_set.index(neighbour)
                        if closed_set[index].f < temp_h:
                            continue

                    neighbour.g = temp_g
                    neighbour.f = temp_g + temp_h
                    heapq.heappush(open_set, (neighbour.f, neighbour))
                    neighbour.prev = current

            closed_set.append(current)


if __name__ == "__main__":
    map = Map()
    start_pos = Vector2(0, 0)
    end_pos = Vector2(100, 180)
    start_time = time.perf_counter()
    path = map.find_path(start_pos, end_pos)
    print(map)
    print(time.perf_counter() - start_time, "\n")
    print("Goal=", 100 // TILE_WIDTH, 180 // TILE_HEIGHT)
    print(len(path))
    for tile in path:
        print(tile.x, tile.y)
