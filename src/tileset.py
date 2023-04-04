from random import random, seed
from typing import List

import pygame as pg
from pygame import Rect, Surface

# from pygame.math import Vector2
from pygame.sprite import Sprite

from constants import (
    GREEN,
    GREY,
    TILE_HEIGHT,
    TILE_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    TileType,
)


class Tile(Sprite):
    """
    A tile is a Rect which is the foundation for the tile map.

    Args: None
    """

    def __init__(self, tile_type: TileType, x: int, y: int, width: int, height: int):
        super().__init__()
        self.type = tile_type
        self.rect = Rect(x, y, width, height)


class Map:
    """
    This is a temporary sample map that can be used just to get
    some of the pathfinding logic down.

    Args: None
    """

    def __init__(self):
        self.map: List[List[Tile]] = []
        self.cols = WINDOW_WIDTH // TILE_WIDTH
        self.rows = WINDOW_HEIGHT // TILE_HEIGHT
        seed(0)

        for row in range(self.rows):
            self.map.append([])
            for col in range(self.cols):
                args = (col * TILE_WIDTH, row * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
                # TODO: Instead of randomly adding NON_PASSABLE lets manually draw them how we want
                # instead.
                self.map[row].append(
                    Tile(TileType.NOT_PASSABLE, *args)
                    if random() < 0.01
                    else Tile(TileType.PASSABLE, *args)
                )
        # start: Vector2, end: Vector2

    def __repr__(self) -> str:
        map_outline = ""
        for row in range(self.rows):
            for col in range(self.cols):
                map_outline += str(self.map[row][col].type.value)
            map_outline += "\n"
        return map_outline

    def draw(self, display_surface: Surface):
        for row in range(self.rows):
            for col in range(self.cols):
                rect = self.map[row][col]
                color = GREEN if rect.type == TileType.PASSABLE else GREY
                pg.draw.rect(display_surface, color, rect)
