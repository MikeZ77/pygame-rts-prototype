import os

import pygame as pg
from pygame import display, time

from constants import WINDOW_HEIGHT, WINDOW_WIDTH
from tileset import Map

# from collections import namedtuple

PROJECT_ROOT = os.path.abspath(os.path.join(__file__, "../.."))
display_surface = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = time.Clock()
FPS = 60

# sprite_sheet = image.load(PROJECT_ROOT + "/assets/sprites/footman.png").convert()

map = Map()
print(map)

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    map.draw(display_surface)
    display.update()
    clock.tick(FPS)


pg.quit()
