# TODO: Refactor this entire module
# TODO: Use gfxdraw for all shapes so that they have anti-aliasing
import time

import pygame as pg
from pygame.math import Vector2

from constants import FPS, MAGENTA, NEON_GREEN, SAND_YELLOW, WINDOW_HEIGHT, WINDOW_WIDTH
from tileset import Map
from unit import Unit

pg.init()

display_surface = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
font = pg.font.SysFont("microsoftsansserif", 16)
clock = pg.time.Clock()
previous_time = time.time()
dt = 0

# sprite_sheet = image.load(PROJECT_ROOT + "/assets/sprites/footman.png").convert()

map = Map()
player = Unit(position=(300, 300), unit="footman")
player_group = pg.sprite.Group(player)
selection_start, selection_current = None, None
selection_end = False
drawing = False

running = True
while running:
    # We get the delta time for each frame (still capped at FPS)
    dt = time.time() - previous_time
    previous_time = time.time()

    for event in pg.event.get():
        keys = pg.key.get_pressed()
        mouse_x, mouse_y = pg.mouse.get_pos()
        mouse_button = pg.mouse.get_pressed()

        if event.type == pg.QUIT:
            running = False

        if keys[pg.K_LSHIFT]:
            # (True, False, False)
            if mouse_button[0]:
                drawing = True
                map.set_barrier(Vector2(mouse_x, mouse_y))

        else:
            drawing = False

        if event.type == pg.KEYDOWN:
            # Press the g key to enable the grid
            if keys[pg.K_g]:
                map.grid = not map.grid

        if event.type == pg.MOUSEBUTTONDOWN:
            if mouse_button[0] and not selection_start:
                selection_start = mouse_x, mouse_y

            if mouse_button[0]:
                # When we click outside the sprite it should de-select that unit
                # TODO: Use a mask later for precise clicks
                if player.rect.collidepoint((mouse_x, mouse_y)):
                    player.is_selected = True
                else:
                    player.is_selected = False

            if mouse_button[2]:
                if player.is_selected:
                    player.path = map.find_path(player.position, Vector2(mouse_x, mouse_y))

        if selection_start:
            selection_current = mouse_x, mouse_y

        # TODO: Set units as selected if inside the bounding box
        if event.type == pg.MOUSEBUTTONUP:
            selection_end = True

    map.draw(display_surface)

    if player.is_selected:
        radius = min(player.rect.width, player.rect.height) // 2
        # TODO: This circle should be fixed when originally set
        pg.draw.circle(display_surface, NEON_GREEN, player.rect.center, radius, 2)

    if player.path and player.state == "IDLE":
        player.follow_path()

    if player.state == "MOVING":
        end_pos = player.path[0]
        pg.draw.line(display_surface, MAGENTA, player.rect.center, end_pos.rect.center, 1)
        pg.draw.circle(display_surface, MAGENTA, end_pos.rect.center, 2)

    player_group.draw(display_surface)
    player.update(dt=dt)

    fps_text = font.render(f"FPS: {clock.get_fps():.2f}", True, SAND_YELLOW)
    display_surface.blit(fps_text, (10, 10))

    if selection_start and selection_current:
        width = abs(selection_current[0] - selection_start[0])
        height = abs(selection_current[1] - selection_start[1])
        box_surface = pg.Surface((width, height))
        box_surface.set_alpha(128)
        box_surface.fill(NEON_GREEN)
        box = pg.Rect(selection_start, (width, height))
        position_offset = selection_start

        # There are 4 cases:
        # Select top -> bottom drag diagonally right (default)
        # Select top -> bottom drag diagonally left
        # Select bottom -> top drag diagonally right
        # Select bottom -> top drag diagonally left

        # TODO: The boarder radius causes isssue when the box is thin. Add a buffer to include the
        # boarder radius s.t. box disapears.

        if selection_current[0] < selection_start[0] and selection_current[1] < selection_start[1]:
            box.topleft = (selection_start[0] - width, selection_start[1] - height)
            position_offset = (selection_start[0] - width, selection_start[1] - height)

        if selection_current[0] < selection_start[0] and selection_current[1] > selection_start[1]:
            box.bottomleft = (selection_start[0] - width, selection_start[1] + height)
            position_offset = (selection_start[0] - width, selection_start[1])

        if selection_current[0] > selection_start[0] and selection_current[1] < selection_start[1]:
            box.topright = (selection_start[0] + width, selection_start[1] - height)
            position_offset = (selection_start[0], selection_start[1] - height)

        if not drawing:
            display_surface.blit(box_surface, position_offset)
            pg.draw.rect(display_surface, NEON_GREEN, box, 2, border_radius=1)

        # print(selection_start, selection_current, selection_end)

        if selection_end:
            # Check if there is a collision with the player rect
            if box.colliderect(player.rect):
                player.is_selected = True

            selection_end = False
            selection_start, selection_current = None, None

    pg.display.update()
    clock.tick(FPS)


pg.quit()
