import pygame as pg
from pygame import Surface
from pygame.math import Vector2


class Camera(pg.sprite.Group):
    def __init__(self, map_surface: Surface):
        self.map_surface = map_surface

        # For camera center
        self.offset = Vector2()
        self.half_width = self.map_surface.get_size()[0] // 2
        self.half_height = self.map_surface.get_size()[2] // 2

        # Box setup
        self.camera_borders = {"left": 200, "right": 200, "top": 100, "bottom": 100}
        self.camera_rect = pg.Rect(
            self.camera_borders["left"],
            self.camera_borders["top"],
            self.camera_borders["left"] + self.camera_borders["right"],
            self.camera_borders["top"] + self.camera_borders["bottom"],
        )

        # camera speed
        self.keyboard_speed = 5
        self.mouse_speed = 0.2

    def mouse_control(self):
        mouse = Vector2(pg.mouse.get_pos())
        mouse_offset_vector = Vector2()

        left_border = self.camera_borders["left"]
        top_border = self.camera_borders["top"]
        right_border = self.map_surface()[0] - self.camera_borders["right"]
        bottom_border = self.map_surface()[1] - self.camera_borders["bottom"]

        if top_border < mouse.y < bottom_border:
            if mouse.x < left_border:
                mouse_offset_vector.x = mouse.x - left_border
                pg.mouse.set_pos((left_border, mouse.y))
            if mouse.x > right_border:
                mouse_offset_vector.x = mouse.x - right_border
                pg.mouse.set_pos((right_border, mouse.y))
        elif mouse.y < top_border:
            if mouse.x < left_border:
                mouse_offset_vector = mouse - pg.math.Vector2(left_border, top_border)
                pg.mouse.set_pos((left_border, top_border))
            if mouse.x > right_border:
                mouse_offset_vector = mouse - pg.math.Vector2(right_border, top_border)
                pg.mouse.set_pos((right_border, top_border))
        elif mouse.y > bottom_border:
            if mouse.x < left_border:
                mouse_offset_vector = mouse - pg.math.Vector2(left_border, bottom_border)
                pg.mouse.set_pos((left_border, bottom_border))
            if mouse.x > right_border:
                mouse_offset_vector = mouse - pg.math.Vector2(right_border, bottom_border)
                pg.mouse.set_pos((right_border, bottom_border))

        if left_border < mouse.x < right_border:
            if mouse.y < top_border:
                mouse_offset_vector.y = mouse.y - top_border
                pg.mouse.set_pos((mouse.x, top_border))
            if mouse.y > bottom_border:
                mouse_offset_vector.y = mouse.y - bottom_border
            pg.mouse.set_pos((mouse.x, bottom_border))

        self.offset += mouse_offset_vector * self.mouse_speed

    def draw(self):
        self.mouse_control()
