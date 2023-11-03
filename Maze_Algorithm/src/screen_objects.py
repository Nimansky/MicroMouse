from __future__ import annotations
from typing import Sequence
import numpy as np
from constants import *
import pygame as pg


class Camera:
    PHYSICAL_VIEWPORT = np.array((200, 200))  # 200cm x 200cm
    WINDOW_SIZE = np.array((1000, 1000))  # 800 x 800 pixel
    position = np.array((0, 0))

    @staticmethod
    def physical_to_pixel(point: np.ndarray | Sequence[float]):
        """Translates Physical positions into pixel space"""
        new_x = Camera.physical_to_pixel_x(point[0])
        new_y = Camera.physical_to_pixel_y(point[1])
        return np.array((new_x, new_y))

    @staticmethod
    def physical_to_pixel_x(x: float):
        fac = Camera.fac()
        return ((x - Camera.position[0]) + Camera.PHYSICAL_VIEWPORT[0] / 2) * fac[0]

    @staticmethod
    def physical_to_pixel_y(y: float):
        fac = Camera.fac()
        return ((y - Camera.position[1]) + Camera.PHYSICAL_VIEWPORT[1] / 2) * fac[1]

    @staticmethod
    def p2p(point: np.ndarray | Sequence[float]):
        return Camera.physical_to_pixel(point)

    @staticmethod
    def p2s(point: Sequence[float] | np.ndarray):
        fac = Camera.fac()
        sx = point[0] * fac[0]
        sy = point[1] * fac[1]
        return np.array((sx, sy))

    @staticmethod
    def physical_to_pixelsize_x(x: float):
        fac = Camera.fac()
        return x * fac[0]

    @staticmethod
    def physical_to_pixelsize_y(y: float):
        fac = Camera.fac()
        return y * fac[1]

    @staticmethod
    def fac() -> np.ndarray:
        return np.array(
            (
                Camera.WINDOW_SIZE[0] / Camera.PHYSICAL_VIEWPORT[0],
                Camera.WINDOW_SIZE[0] / Camera.PHYSICAL_VIEWPORT[1],
            )
        )

    @staticmethod
    def move(x, y):
        Camera.position[0] += x
        Camera.position[1] += y

    @staticmethod
    def move_to(x, y):
        Camera.position[0] = x
        Camera.position[1] = y



class ScreenObject(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, *groups):
        self._self_group = pg.sprite.GroupSingle()
        super().__init__(*groups, self._self_group)
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self.image = pg.Surface((self.wwidth, self.wheight), pg.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.wx, self.wy))
        self.draw = self._self_group.draw
        self._color_key = None
        self._update_image()

    @staticmethod
    def modified_state(func):
        def wrapper(self: ScreenObject, *args, **kwargs):
            res = func(self, *args, **kwargs)
            self._update_image()
            return res

        return wrapper

    @property
    def x(self) -> float:
        """The X coordinate of the object in centimeter Space

        Returns
        -------
        float
            x position in cm
        """
        return self._x

    @x.setter
    def x(self, val: float):
        """Setting the X coordinate of the object in centimeter Space

        Parameters
        ----------
        val : float
            x coordinate cm
        """
        self._x = val
        self._update_rect()

    @property
    def y(self) -> float:
        """The Y coordinate of the object in centimeter Space

        Returns
        -------
        float
            y position in cm
        """
        return self._y

    @y.setter
    def y(self, val: float):
        """Setting the Y coordinate of the object in centimeter Space

        Parameters
        ----------
        val : float
            y coordinate cm
        """
        self._y = val
        self._update_rect()

    @property
    def wx(self) -> float:
        """The X coordinate of the object in pixel Space

        Returns
        -------
        float
            x position in pixel space
        """
        return np.ceil(Camera.physical_to_pixel_x(self._x))

    @property
    def wy(self) -> float:
        """The Y coordinate of the object in pixel Space

        Returns
        -------
        float
            y position in pixel space
        """
        return np.ceil(Camera.physical_to_pixel_y(self._y))

    @property
    def xy(self):
        """The X,Y coordinate of the object in centimeter Space

        Returns
        -------
        tuple[float,float]
            x,y position in cm
        """
        return np.array((self.x, self.y))

    @property
    def wxy(self):
        """The X,Y coordinate of the object in pixel Space

        Returns
        -------
        tuple[float,float]
            x,y position in pixel space
        """
        return np.array((self.wx, self.wy))

    @property
    def width(self) -> float:
        """The width of the object in centimeter Space

        Returns
        -------
        float
            width in cm
        """
        return self._width

    @width.setter
    def width(self, val: float):
        """Setting the width of the object in centimeter Space

        Parameters
        ----------
        val : float
            width in cm
        """
        self._width = val
        self._update_rect_surf()

    @property
    def height(self) -> float:
        """The height of the object in centimeter Space

        Returns
        -------
        float
            height in cm
        """
        return self._height

    @height.setter
    def height(self, val: float):
        """Setting the height of the object in centimeter Space

        Parameters
        ----------
        val : float
            height in cm
        """
        self._height = val
        self._update_rect_surf()

    @property
    def wwidth(self) -> float:
        """The width of the object in pixel Space

        Returns
        -------
        float
            width in pixel space
        """
        return np.ceil(Camera.physical_to_pixelsize_x(self._width))

    @property
    def wheight(self) -> float:
        """The height of the object in pixel Space

        Returns
        -------
        float
            height in pixel space
        """
        return np.ceil(Camera.physical_to_pixelsize_y(self._height))

    @property
    def size(self):
        """The width,height of the object in centimeter Space

        Returns
        -------
        tuple[float,float]
            width,height in cm
        """
        return np.array((self.width, self.height))

    @property
    def wsize(self):
        """The width,height of the object in pixel Space

        Returns
        -------
        tuple[float,float]
            width,height in pixel space
        """
        return np.array((self.wwidth, self.wheight))

    def _update_rect(self):
        """
        Update the object's rect attribute with the new x,y coordinates.
        in pixel space
        """
        self.rect = self.image.get_rect(center=(self.wx, self.wy))

    def _update_surf(self):
        """
        Update the object's surf attribute with the new width,height.
        in pixel space
        """
        self.image = pg.Surface((self.wwidth, self.wheight))
        self._update_image()

    def _update_rect_surf(self):
        """
        Update the object's rect attribute with the new x,y coordinates.
        Update the object's surf attribute with the new width,height.
        in pixel space
        """
        self._update_rect()
        self._update_surf()

    def draw_line(
        self,
        start: np.ndarray | Sequence[float],
        end: np.ndarray | Sequence[float],
        color: pg.Color = WHITE,
        stroke_width=3,
    ):
        """Draw a line on the object

        Parameters
        ----------
        start : np.ndarray | Sequence[float]
            start point in pixels
        end : np.ndarray | Sequence[float]
            end point in pixels
        color : pg.Color, optional
            color of the line, by default WHITE
        stroke_width : int, optional
            width of the line, by default 3
        """
        # start = tuple(Camera.p2s(start))
        # end = tuple(Camera.p2s(end))
        pg.draw.line(self.image, color, tuple(start), tuple(end), stroke_width)

    def draw_rect(
        self,
        pos: np.ndarray | Sequence[float],
        size: np.ndarray | Sequence[float],
        color: pg.Color = WHITE,
    ):
        """Draw a rectangle on the object

        Parameters
        ----------
        pos : np.ndarray | Sequence[float]
            position of the rectangle in pixels
        size : np.ndarray | Sequence[float]
            size of the rectangle in pixels
        color : pg.Color, optional
            color of the rectangle, by default WHITE
        """
        pg.draw.rect(self.image, color, [pos[0], pos[1], size[0], size[1]])

    def draw_circle(
        self, pos: np.ndarray | Sequence[float], radius: float, color: pg.Color = WHITE
    ):
        """Draw a circle on the object

        Parameters
        ----------
        pos : np.ndarray | Sequence[float]
            position of the circle in pixels
        radius : float
            radius of the circle in cm
        color : pg.Color, optional
            color of the circle, by default WHITE
        """
        radius = Camera.physical_to_pixelsize_x(radius)
        pg.draw.circle(self.image, color, tuple(pos), radius)

    def draw_arc(self, pos, radius, start_angle, end_angle, color=WHITE, width=1):
        """Draw an arc on the object

        Parameters
        ----------
        pos : np.ndarray
            position of the arc in pixels
        radius : float
            radius of the arc in cm
        start_angle : float
            start angle of the arc in degree
        end_angle : float
            end angle of the arc in degree
        color : pg.Color, optional
            color of the arc, by default WHITE
        width : int, optional
            width of the arc, by default 1
        """
        radius = Camera.physical_to_pixelsize_x(radius)
        pg.draw.arc(self.image, color, tuple(pos), start_angle, end_angle, width)

    def draw_image(self, image: pg.Surface):
        """Draw an image on the object

        Parameters
        ----------
        image : pg.Surface
            image to draw
        """
        pg.transform.scale(image, (self.wwidth, self.wheight), self.image)

    def set_color_key(self, color: pg.Color):
        """Set the color key of the object

        Parameters
        ----------
        color : pg.Color
            color to set
        """
        self._color_key = color

    def draw_image_at(self, image: pg.Surface, pos: np.ndarray | Sequence[float]):
        """Draw an image on the object

        Parameters
        ----------
        image : pg.Surface
            image to draw
        pos : np.ndarray | Sequence[float]
            position of the image in pixels
        """
        self.image.blit(image, tuple(pos))

    def rotate_image(self, angle: float):
        """Rotate the object

        Parameters
        ----------
        angle : float
            angle in degree
        """
        # clear the current image and put in a center rotated variant of the current image
        tmp = pg.Surface((self.wwidth, self.wheight), pg.SRCALPHA)
        rotated = pg.transform.rotate(self.image, angle)
        rect = rotated.get_rect(center=(self.wwidth / 2, self.wheight / 2))
        tmp.blit(rotated, rect)
        self.image = tmp
        self._update_rect()

    def fill_image(self, color: pg.Color):
        """Fill the object with a color

        Parameters
        ----------
        color : pg.Color
            color to fill
        """
        self.image.fill(color)

    def _update_image(self):
        """Update the image of the object"""
        self.create_image(self.wwidth, self.wheight, Camera.fac()[0])

    def update(self, *args, **kwargs):
        """Update the object"""
        self.process_events()

    def create_image(self, width: float, height: float, fac:float):
        """Creates a sprite for the object
        Use the draw functions to draw on the sprite

        Parameters
        ----------
        width : float
            width in pixels
        height : float
            height in pixels
        """
        raise NotImplementedError

    def process_events(self):
        """Process events"""
        pass

    def is_hovered(self):
        """Check if the object is hovered by the mouse

        Returns
        -------
        bool
            True if the mouse is hovering over the object
        """
        return self.rect.collidepoint(pg.mouse.get_pos())
