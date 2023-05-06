import json
import random
from typing import List, Tuple, Union

import pygame as pg
from pygame import Surface
from pygame.math import Vector2
from pygame.mixer import Sound
from transitions import Machine

from constants import MAGENTA, NEON_GREEN, PROJECT_ROOT
from tileset import Tile
from types_ import SpriteAnimationType as Animation


class Unit(pg.sprite.Sprite):
    SPRITE_FOLDER = PROJECT_ROOT + "/assets/sprites/"
    SOUND_FOLDER = PROJECT_ROOT + "/assets/sounds/"
    METADATA_FILE = SPRITE_FOLDER + "metadata.json"
    states = ["IDLE", "MOVING"]

    animation_lookup = {
        (0, -1): Animation.VERTICAL_UP,
        (1, 0): Animation.HORIZONTAL_RIGHT,
        (0, 1): Animation.VERTICAL_DOWN,
        (-1, 0): Animation.HORIZONTAL_LEFT,
        (1, -1): Animation.DIAGONAL_UP_RIGHT,
        (1, 1): Animation.DIAGONAL_DOWN_RIGHT,
        (-1, 1): Animation.DIAGONAL_DOWN_LEFT,
        (-1, -1): Animation.DIAGONAL_UP_LEFT,
    }

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
        self.sound_effects: dict[list[Sound]] = {"select": [], "move": []}
        self.machine = Machine(model=self, states=Unit.states, initial="IDLE")
        self.machine.add_transition(trigger="follow_path", source="IDLE", dest="MOVING")
        self.machine.add_transition(trigger="finished_path", source="MOVING", dest="IDLE")
        self._path: Union[List[Tile], None] = None
        self.next_tile = None
        self._is_selected = False
        self.image = None
        self.rect = None
        self._load_data(sheet=unit)

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, new_value: bool):
        if new_value:
            self._play_sound("select")
        self._is_selected = new_value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_value: list[Tile]):
        if self._path is not new_value:
            self._play_sound("move")
        self._path = new_value

    def _load_data(self, *, sheet: str):
        # Load unit sprite sheet
        sprite_sheet_path = Unit.SPRITE_FOLDER + sheet + ".png"
        sprite_sheet = pg.image.load(sprite_sheet_path).convert_alpha()

        # Load metadata
        with open(Unit.METADATA_FILE, "r") as file:
            metadata = json.load(file)
            unit_metadata = list(filter(lambda unit: unit["sheet"] == sheet, metadata))[0]

        # Load sound files
        sound_fle_path = Unit.SOUND_FOLDER + sheet
        sounds = unit_metadata["sounds"]
        for key, value in self.sound_effects.items():
            for sound in sounds[key]:
                value.append(pg.mixer.Sound(sound_fle_path + "/" + sound))

        # Set unit properties
        unit_properties = unit_metadata["properties"]
        self.__dict__.update(*unit_properties)

        # Set sprite sheet data
        sprite_meta_data = unit_metadata["sprites"]
        for data in sprite_meta_data:
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

    def _play_sound(self, sound: str):
        print(sound)
        select_sounds = self.sound_effects[sound]
        random_sound = random.randint(0, len(select_sounds) - 1)
        select_sounds[random_sound].play()

    def update(self, *, dt: float):
        """
        Updates are received by the GameManager and handled here based on the current state.
        """
        if self.state == "MOVING":
            if not self.next_tile:
                self.next_tile = self._path.pop()

            next_position = self.next_tile.rect.center
            direction: Vector2 = round((Vector2(next_position) - self.position).normalize())
            animation = self.animation_lookup.get(tuple(direction))

            # print(direction, self.position, next_position)
            # print(direction.length())

            # TODO: Need to normalize diag vectors. Use enum values to check using > value.
            self.position += dt * self.speed * direction
            self._cycle_sprite_frame(animation, dt)

            if tuple(round(self.position)) == next_position:
                if len(self._path):
                    self.next_tile.prev = None
                    self.next_tile.is_path = False
                    self.next_tile = None
                else:
                    self.state = "IDLE"

        self.rect.center = (round(self.position.x), round(self.position.y))

    def draw(self, screen: Surface, end_pos: Tile):
        if self._is_selected:
            # TODO: This circle should be fixed when see metadata
            pg.draw.circle(screen, NEON_GREEN, self.rect.center, self.selection_radius, 2)

        if self._path and self.state == "IDLE":
            self.follow_path()

        if self.state == "MOVING":
            pg.draw.line(screen, MAGENTA, self.rect.center, end_pos.rect.center, 1)
            pg.draw.circle(screen, MAGENTA, end_pos.rect.center, 2)
