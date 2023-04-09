import json
from typing import List, Tuple, Union

import pygame as pg
from pygame import Surface
from pygame.math import Vector2
from transitions import Machine

from constants import PROJECT_ROOT
from tileset import Tile
from types_ import SpriteAnimationType as Animation


class Unit(pg.sprite.Sprite):
    SPRITE_FOLDER = PROJECT_ROOT + "/assets/sprites/"
    METADATA_FILE = SPRITE_FOLDER + "metadata.json"
    states = ["IDLE", "MOVING"]

    def __init__(self, *, position: Tuple[int, int], unit: str, speed: int = 40):
        super().__init__()

        self.image = None
        self.position = Vector2(*position)
        self.speed = speed
        self.frame_duration = 0.1
        self.frame_index = 0
        self.frame_time = 0.0
        self.frame_type = Animation.VERTICAL_DOWN
        self.frames = {
            Animation.VERTICAL_UP: [],
            Animation.VERTICAL_DOWN: [],
            Animation.HORIZONTAL_LEFT: [],
            Animation.HORIZONTAL_RIGHT: [],
            Animation.DIAGONAL_UP_LEFT: [],
            Animation.DIAGONAL_UP_RIGHT: [],
            Animation.DIAGONAL_DOWN_LEFT: [],
            Animation.DIAGONAL_DOWN_RIGHT: [],
        }
        self.machine = Machine(model=self, states=Unit.states, initial="IDLE")
        self.machine.add_transition(trigger="follow_path", source="IDLE", dest="MOVING")
        self.machine.add_transition(trigger="finished_path", source="MOVING", dest="IDLE")
        self.path: Union[List[Tile], None] = None
        self.is_selected = False
        self.image = None
        self.rect = None
        self._load_sprite_sheet(sheet=unit)

    def _load_sprite_sheet(self, *, sheet: str):
        sprite_sheet_path = Unit.SPRITE_FOLDER + sheet + ".png"
        sprite_sheet = pg.image.load(sprite_sheet_path).convert_alpha()
        with open(Unit.METADATA_FILE, "r") as file:
            metadata = json.load(file)
            unit_metadata = list(filter(lambda unit: unit["sheet"] == sheet, metadata))[0][
                "sprites"
            ]

        for data in unit_metadata:
            type = data["type"]
            rect = pg.Rect(data["x"], data["y"], data["width"], data["height"])
            sprite = sprite_sheet.subsurface(rect)
            self.frames[Animation(type)].append(sprite)

            if Animation.DIAGONAL_UP_RIGHT == type:
                self.frames[Animation.DIAGONAL_UP_LEFT].append(
                    pg.transform.flip(sprite, flip_x=True, flip_y=False)
                )

            if Animation.DIAGONAL_DOWN_RIGHT == type:
                self.frames[Animation.DIAGONAL_DOWN_LEFT].append(
                    pg.transform.flip(sprite, flip_x=True, flip_y=False)
                )

            if Animation.HORIZONTAL_RIGHT == type:
                self.frames[Animation.HORIZONTAL_LEFT].append(
                    pg.transform.flip(sprite, flip_x=True, flip_y=False)
                )

        # Select a starting defualt image
        self.image: Surface = self.frames[self.frame_type][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (round(self.position.x), round(self.position.y))

    def _cycle_sprite_frame(self, direction: Animation, dt: float):
        # Determine if the current frame has expired
        self.frame_time += dt
        next_frame = self.frame_time > self.frame_duration
        if next_frame:
            # Reset the frame time count
            self.frame_time = 0.0
            # If the directon vector has not changed just get the next index
            if direction == self.frame_type:
                self.frame_index = (self.frame_index + 1) % len(self.frames[self.frame_type])
            # If it has start the index at 0 and use the new direction image
            if direction != self.frame_type:
                self.frame_type = direction
                self.frame_index = 0
            # Select the new image to render
            self.image: Surface = self.frames[self.frame_type][self.frame_index]
            self.rect = self.image.get_rect()

    def update(self, *, dt: float):
        # Our direction vectors
        direction_up = Vector2(0, -1)
        direction_up_right = Vector2(1, -1)
        direction_right = Vector2(1, 0)
        direction_down_right = Vector2(1, 1)
        direction_down = Vector2(0, 1)
        direction_down_left = Vector2(-1, 1)
        direction_left = Vector2(-1, 0)
        direction_up_left = Vector2(-1, -1)

        keys = pg.key.get_pressed()
        # new_pos = old_pos + (dt * direction_vector * speed)
        # new_pos = old_pos + (dt * velocity)
        if keys[pg.K_UP] and keys[pg.K_RIGHT]:
            self.position += dt * self.speed * direction_up_right.normalize()
            self._cycle_sprite_frame(Animation.DIAGONAL_UP_RIGHT, dt)

        elif keys[pg.K_DOWN] and keys[pg.K_RIGHT]:
            self.position += dt * self.speed * direction_down_right.normalize()
            self._cycle_sprite_frame(Animation.DIAGONAL_DOWN_RIGHT, dt)

        elif keys[pg.K_DOWN] and keys[pg.K_LEFT]:
            self.position += dt * self.speed * direction_down_left.normalize()
            self._cycle_sprite_frame(Animation.DIAGONAL_DOWN_LEFT, dt)

        elif keys[pg.K_UP] and keys[pg.K_LEFT]:
            self.position += dt * self.speed * direction_up_left.normalize()
            self._cycle_sprite_frame(Animation.DIAGONAL_UP_LEFT, dt)

        elif keys[pg.K_RIGHT]:
            self.position += dt * self.speed * direction_right
            self._cycle_sprite_frame(Animation.HORIZONTAL_RIGHT, dt)

        elif keys[pg.K_LEFT]:
            self.position += dt * self.speed * direction_left
            self._cycle_sprite_frame(Animation.HORIZONTAL_LEFT, dt)

        elif keys[pg.K_UP]:
            self.position += dt * self.speed * direction_up
            self._cycle_sprite_frame(Animation.VERTICAL_UP, dt)

        elif keys[pg.K_DOWN]:
            self.position += dt * self.speed * direction_down
            self._cycle_sprite_frame(Animation.VERTICAL_DOWN, dt)

        self.rect.center = (round(self.position.x), round(self.position.y))
