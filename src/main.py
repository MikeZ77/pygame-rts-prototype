# TODO: Refactor this entire module
# TODO: Use gfxdraw for all shapes so that they have anti-aliasing
import time

import pygame as pg
from pygame import Rect, Surface
from pygame.math import Vector2

from constants import NEON_GREEN, SAND_YELLOW, WINDOW_HEIGHT, WINDOW_WIDTH
from tileset import Map
from unit import Unit


class App:
    def __init__(self):
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.font = pg.font.SysFont("microsoftsansserif", 16)
        self.clock = pg.time.Clock()
        self.fps = 60
        self.running = True
        self.map = Map()
        self.player = Unit(position=(300, 300), unit="footman")
        self.player_group = pg.sprite.Group(self.player)
        self.selection_start = None
        self.selection_current = None
        self.selection_end = False
        self.box_surface: Surface = None
        self.box: Rect = None
        self.position_offset = None
        self.drawing = False
        self.end_pos = None

    def handle_input(self):
        """
        Handles useer input from the event loop.
        """
        for event in pg.event.get():
            mouse_left, _, mouse_right = pg.mouse.get_pressed()
            mouse_x, mouse_y = pg.mouse.get_pos()
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
                    self.handle_selection_box_create(mouse_x, mouse_y)
                    self.handle_unit_selection(mouse_x, mouse_y, mouse_left)

                # Handle all mouse right click actions
                if mouse_right:
                    self.player.is_selected and self.handle_unit_move(mouse_x, mouse_y)

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
        print(self.map.count_tiles_with_prev())
        # TODO: Move to state class when we have more than one "player" unit
        self.end_pos = self.player.path[0]

    def update_tile_hole(self):
        mouse_left, _, _ = pg.mouse.get_pressed()
        if self.drawing and mouse_left:
            self.map.set_barrier(Vector2(*pg.mouse.get_pos()))

    def update_selection_current(self):
        if self.selection_start:
            self.selection_current = pg.mouse.get_pos()

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
            self.screen.blit(self.box_surface, self.position_offset)
            pg.draw.rect(self.screen, NEON_GREEN, self.box, 2, border_radius=1)

    def update(self, dt: float):
        """
        Updates all game objects for a unit of delta time.
        """
        self.player.update(dt=dt)
        self.update_tile_hole()
        self.update_selection_current()
        self.update_selection_box()

    def render(self):
        """
        Renders all objects to the display surface.
        """
        self.map.draw(self.screen)
        self.player.draw(self.screen, self.end_pos)
        self.player_group.draw(self.screen)
        self.render_selection_box()
        fps_text = self.font.render(f"FPS: {self.clock.get_fps():.2f}", True, SAND_YELLOW)
        self.screen.blit(fps_text, (10, 10))
        pg.display.update()

    def game_loop(self):
        dt = 0
        t_prev = time.time()
        while self.running:
            dt = time.time() - t_prev
            t_prev = time.time()
            self.handle_input()
            self.update(dt)
            self.render()
            self.clock.tick(self.fps)


def main():
    pg.init()
    App().game_loop()
    pg.quit()


if __name__ == "__main__":
    main()


# display_surface = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
# font = pg.font.SysFont("microsoftsansserif", 16)
# clock = pg.time.Clock()
# previous_time = time.time()
# dt = 0

# # sprite_sheet = image.load(PROJECT_ROOT + "/assets/sprites/footman.png").convert()

# map = Map()
# player = Unit(position=(300, 300), unit="footman")
# player_group = pg.sprite.Group(player)
# selection_start, selection_current = None, None
# end_pos = None
# selection_end = False
# drawing = False

# running = True
# while running:
#     # We get the delta time for each frame (still capped at FPS)
#     dt = time.time() - previous_time
#     previous_time = time.time()

#     for event in pg.event.get():
#         keys = pg.key.get_pressed()
#         mouse_x, mouse_y = pg.mouse.get_pos()
#         mouse_button = pg.mouse.get_pressed()

#         if event.type == pg.QUIT:
#             running = False

#         if keys[pg.K_LSHIFT]:
#             # (True, False, False)
#             if mouse_button[0]:
#                 drawing = True
#                 map.set_barrier(Vector2(mouse_x, mouse_y))

#         else:
#             drawing = False

#         if event.type == pg.KEYDOWN:
#             # Press the g key to enable the grid
#             if keys[pg.K_g]:
#                 map.grid = not map.grid

#         if event.type == pg.MOUSEBUTTONDOWN:
#             if mouse_button[0] and not selection_start:
#                 selection_start = mouse_x, mouse_y

#             if mouse_button[0]:
#                 # When we click outside the sprite it should de-select that unit
#                 # TODO: Use a mask later for precise clicks
#                 if player.rect.collidepoint((mouse_x, mouse_y)):
#                     player.is_selected = True
#                 else:
#                     player.is_selected = False

#             if mouse_button[2]:
#                 if player.is_selected:
#                     # Do not show the previous path
#                     if player.path:
#                         for tile in player.path:
#                             tile.is_path = False

#                     start_time = time.perf_counter()
#                     player.path = map.find_path(player.position, Vector2(mouse_x, mouse_y))
#                     print(time.perf_counter() - start_time, "\n")
#                     print(map.count_tiles_with_prev())
#                     end_pos = player.path[0]

#         if selection_start:
#             selection_current = mouse_x, mouse_y

#         # TODO: Set units as selected if inside the bounding box
#         if event.type == pg.MOUSEBUTTONUP:
#             if event.button == 1:
#                 selection_end = True

#     map.draw(display_surface)

#     if player.is_selected:
#         radius = min(player.rect.width, player.rect.height) // 2
#         # TODO: This circle should be fixed when originally set
#         # Probably easiest to just have this set in the metadata
#         pg.draw.circle(display_surface, NEON_GREEN, player.rect.center, radius, 2)

#     if player.path and player.state == "IDLE":
#         player.follow_path()

#     if player.state == "MOVING":
#         pg.draw.line(display_surface, MAGENTA, player.rect.center, end_pos.rect.center, 1)
#         pg.draw.circle(display_surface, MAGENTA, end_pos.rect.center, 2)

#     # print("Player state", player.state)
#     # print(selection_start, selection_current)
#     # print(player.is_selected)

#     player_group.draw(display_surface)
#     player.update(dt=dt)

#     fps_text = font.render(f"FPS: {clock.get_fps():.2f}", True, SAND_YELLOW)
#     display_surface.blit(fps_text, (10, 10))

#     if selection_start and selection_current:
#         width = abs(selection_current[0] - selection_start[0])
#         height = abs(selection_current[1] - selection_start[1])
#         box_surface = pg.Surface((width, height))
#         box_surface.set_alpha(128)
#         box_surface.fill(NEON_GREEN)
#         box = pg.Rect(selection_start, (width, height))
#         position_offset = selection_start

#         # There are 4 cases:
#         # Select top -> bottom drag diagonally right (default)
#         # Select top -> bottom drag diagonally left
#         # Select bottom -> top drag diagonally right
#         # Select bottom -> top drag diagonally left

#         # TODO: The boarder radius causes isssue when the box is thin. Add a buffer to include the
#         # boarder radius s.t. box disapears.

#         if selection_current[0] < selection_start[0] and selection_current[1] < selection_start[1]:
#             box.topleft = (selection_start[0] - width, selection_start[1] - height)
#             position_offset = (selection_start[0] - width, selection_start[1] - height)

#         if selection_current[0] < selection_start[0] and selection_current[1] > selection_start[1]:
#             box.bottomleft = (selection_start[0] - width, selection_start[1] + height)
#             position_offset = (selection_start[0] - width, selection_start[1])

#         if selection_current[0] > selection_start[0] and selection_current[1] < selection_start[1]:
#             box.topright = (selection_start[0] + width, selection_start[1] - height)
#             position_offset = (selection_start[0], selection_start[1] - height)

#         if not drawing:
#             display_surface.blit(box_surface, position_offset)
#             pg.draw.rect(display_surface, NEON_GREEN, box, 2, border_radius=1)

#         # print(selection_start, selection_current, selection_end)

#         if selection_end:
#             # Check if there is a collision with the player rect
#             if box.colliderect(player.rect):
#                 player.is_selected = True

#             selection_end = False
#             selection_start, selection_current = None, None

#     pg.display.update()
#     clock.tick(FPS)


# pg.quit()
