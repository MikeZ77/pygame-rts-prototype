# TODO: Refactor this entire module
# TODO: Use gfxdraw for all shapes so that they have anti-aliasing
import time
from typing import Tuple

import pygame as pg
from pygame import Rect, Surface
from pygame.math import Vector2

from constants import (
    GREEN,
    MAP_HEIGHT,
    MAP_WIDTH,
    NEON_GREEN,
    SAND_YELLOW,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from tileset import Map
from unit import Unit


class App:
    def __init__(self):
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.camera_rect = pg.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.map_surface = Surface((MAP_WIDTH, MAP_HEIGHT))
        self.camera_speed = 2
        self.camera_buffer = 5
        self.map = Map(self.map_surface)
        self.font = pg.font.SysFont("microsoftsansserif", 16)
        self.clock = pg.time.Clock()
        self.fps = 60
        self.running = True
        self.player = Unit(position=(300, 300), unit="footman")
        self.player_group = pg.sprite.Group(self.player)
        self.selection_start: Tuple[int, int] = None
        self.selection_current: Tuple[int, int] = None
        self.selection_end: Tuple[int, int] = False
        self.position_offset: Tuple[int, int] = None
        self.end_pos: Tuple[int, int] = None
        self.box_surface: Surface = None
        self.box: Rect = None
        self.drawing = False

    def _get_mouse_offset(self) -> Tuple[bool, bool]:
        """Helper method that gets the mouse offset based on the camera position"""
        (mouse_x, mouse_y) = pg.mouse.get_pos()
        return (mouse_x - self.camera_rect.left, mouse_y - self.camera_rect.top)

    def handle_input(self):
        """
        Handles useer input from the event loop.
        """
        for event in pg.event.get():
            mouse_left, _, mouse_right = pg.mouse.get_pressed()
            # mouse_x, mouse_y = pg.mouse.get_pos()
            # keys = pg.key.get_pressed()

            if event.type == pg.QUIT:
                self.running = False

            if event.type == pg.KEYDOWN:
                # Toggles a grid view of the map for illustrative purposes
                if event.key == pg.K_g:
                    self.map.grid = not self.map.grid

                # Turn drawing mode on
                if event.key == pg.K_LSHIFT:
                    self.drawing = True

            if event.type == pg.KEYUP:
                if event.key == pg.K_LSHIFT:
                    self.drawing = False

            if event.type == pg.MOUSEBUTTONDOWN:
                # Handle all mouse left click actions
                if mouse_left:
                    self.handle_selection_box_create(*self._get_mouse_offset())
                    self.handle_unit_selection(*self._get_mouse_offset(), mouse_left)

                # Handle all mouse right click actions
                if mouse_right:
                    self.player.is_selected and self.handle_unit_move(*self._get_mouse_offset())

            if event.type == pg.MOUSEBUTTONUP:
                event.button == 1 and self.handle_selection_box_end()

    def handle_selection_box_create(self, mouse_x: int, mouse_y: int):
        """Sets the starting x,y pixel position for the selection box"""
        if not self.selection_start:
            self.selection_start = mouse_x, mouse_y

    def handle_selection_box_end(self):
        self.selection_end = True

    def handle_unit_selection(self, mouse_x: int, mouse_y: int, mouse_left: bool):
        """Checks if a unit is selected and sets the unit is_selected property"""
        self.player.is_selected = (
            True if self.player.rect.collidepoint((mouse_x, mouse_y)) else False
        )

    def handle_unit_move(self, mouse_x, mouse_y):
        """Updates a unit with a new movement path"""
        # TODO: Remove this
        if self.player.path:
            for tile in self.player.path:
                tile.is_path = False

        start_time = time.perf_counter()
        self.player.path = self.map.find_path(self.player.position, Vector2(mouse_x, mouse_y))
        print(time.perf_counter() - start_time, "\n")
        # TODO: Move to state class when we have more than one "player" unit
        self.end_pos = self.player.path[0]

    def update_camera(self, dt: float):
        mouse_x, mouse_y = pg.mouse.get_pos()
        width, height = WINDOW_WIDTH, WINDOW_HEIGHT
        map_rect = self.map_surface.get_rect()
        # print(mouse_x, mouse_y)
        # We need to keep track of where we have gone relative to the map surface
        # For now we will assume the camera always starts top left of the map
        left_offset = map_rect.left - self.camera_rect.left
        right_offset = map_rect.right - self.camera_rect.right
        top_offset = map_rect.top - self.camera_rect.top
        bottom_offset = map_rect.bottom - self.camera_rect.bottom
        # TODO: Corners, right now the speed is doubled
        if (
            mouse_x in range(width - self.camera_buffer, width)
            and left_offset >= 0
            and right_offset < map_rect.right
        ):
            self.camera_rect.move_ip(-self.camera_speed, 0)

        if (
            mouse_y in range(height - self.camera_buffer, height)
            and top_offset >= 0
            and bottom_offset < map_rect.bottom
        ):
            self.camera_rect.move_ip(0, -self.camera_speed)

        if mouse_x in range(0, self.camera_buffer) and left_offset > 0:
            self.camera_rect.move_ip(self.camera_speed, 0)

        if mouse_y in range(0, self.camera_buffer) and top_offset > 0:
            self.camera_rect.move_ip(0, self.camera_speed)

    def update_tile_hole(self):
        mouse_left, _, _ = pg.mouse.get_pressed()
        if self.drawing and mouse_left:
            self.map.add_hole(Vector2(*self._get_mouse_offset()))

    def update_selection_current(self):
        if self.selection_start:
            self.selection_current = self._get_mouse_offset()

    def update_selection_box(self):
        if self.selection_start and self.selection_current:
            start_x, start_y, current_x, current_y = self.selection_start + self.selection_current
            width, height = abs(current_x - start_x), abs(current_y - start_y)
            self.box_surface = pg.Surface((width, height))
            self.box_surface.set_alpha(128)
            self.box_surface.fill(NEON_GREEN)
            self.box = pg.Rect(self.selection_start, (width, height))
            self.position_offset = self.selection_start  # Default case

            if current_x < start_x and current_y < start_y:
                self.box.topleft = (start_x - width, start_y - height)
                self.position_offset = (start_x - width, start_y - height)

            if current_x < start_x and current_y > start_y:
                self.box.bottomleft = (start_x - width, start_y + height)
                self.position_offset = (start_x - width, start_y)

            if current_x > start_x and current_y < start_y:
                self.box.topright = (start_x + width, start_y - height)
                self.position_offset = (start_x, start_y - height)

            # Selection end from the MOUSEBUTTONUP event
            if self.selection_end:
                # If there is a collision with a unit rect set as selected
                if self.box.colliderect(self.player.rect):
                    self.player.is_selected = True

                self.selection_start, self.selection_current = None, None
                self.selection_end = False

    def render_selection_box(self):
        # Disable selection box when drawing holes
        if self.selection_start and self.selection_current and not self.drawing:
            self.map_surface.blit(self.box_surface, self.position_offset)
            pg.draw.rect(self.map_surface, NEON_GREEN, self.box, 2, border_radius=1)

    def update(self, dt: float):
        """
        Updates all game objects for a unit of delta time.
        """
        self.update_camera(dt=dt)
        self.player.update(dt=dt)
        self.update_tile_hole()
        self.update_selection_current()
        self.update_selection_box()

    def render(self):
        """
        Renders all objects to the display surface.
        """

        # For now center the screen (camera) at the topleft of the map surface
        # self.screen.blit(self.map_surface, (0, 0))
        self.screen.blit(self.map_surface, self.camera_rect)
        self.map_surface.fill(GREEN)
        self.map.draw(self.map_surface, self.camera_rect)
        self.player.draw(self.map_surface, self.end_pos)
        self.player_group.draw(self.map_surface)
        self.render_selection_box()
        fps_text = self.font.render(f"FPS: {self.clock.get_fps():.2f}", True, SAND_YELLOW)
        self.screen.blit(fps_text, (10, 10))
        pg.display.update()

    def game_loop(self):
        dt = 0
        t_prev = time.time()
        pg.event.set_grab(True)
        while self.running:
            dt = time.time() - t_prev
            t_prev = time.time()
            self.handle_input()
            self.update(dt)
            self.render()
            self.clock.tick(self.fps)


def main():
    pg.init()
    pg.mixer.init()
    App().game_loop()
    pg.quit()


if __name__ == "__main__":
    main()
