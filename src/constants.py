from enum import Enum

# Environment
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 600
TILE_WIDTH = 8
TILE_HEIGHT = 8

# Colors
GREEN = (0, 154, 23)
GREY = (220, 220, 220)


# Enums
class TileType(Enum):
    NOT_PASSABLE = 0
    PASSABLE = 1


class SpriteAction(Enum):
    VERTICAL_UP = 1
    HORIZONTAL = 2
    DIAGONAL_UP = 3
    DIAGONAL_DOWN = 4
    VERTICAL_DOWN = 5
    VERTICAL_ATTACKING = 6
    HORIZONTAL_ATTACKING = 7
    DIAGONAL_UP_ATTACKING = 8
    DIAGONAL_DOWN_ATTACKING = 9
