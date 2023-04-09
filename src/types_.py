from enum import Enum, IntEnum

# from typing import Tuple


# Enums
class TileType(Enum):
    NOT_PASSABLE = 0
    PASSABLE = 1


class SpriteAnimationType(IntEnum):
    VERTICAL_UP = 1
    HORIZONTAL_RIGHT = 2
    DIAGONAL_UP_RIGHT = 3
    DIAGONAL_DOWN_RIGHT = 4
    VERTICAL_DOWN = 5
    HORIZONTAL_LEFT = 6
    DIAGONAL_UP_LEFT = 7
    DIAGONAL_DOWN_LEFT = 8
    # VERTICAL_ATTACKING = 6
    # HORIZONTAL_ATTACKING = 7
    # DIAGONAL_UP_ATTACKING = 8
    # DIAGONAL_DOWN_ATTACKING = 9

    # TODO: Implement __eq__ with enum
