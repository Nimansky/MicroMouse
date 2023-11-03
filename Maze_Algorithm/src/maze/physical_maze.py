from typing import Any
from screen_objects import ScreenObject
import pygame as pg
from constants import *
from maze.maze_builder import MazeBuilder


class PhysicalBox(ScreenObject):
    def __init__(
        self, paths: str, x: float, y: float, width: float, height: float, *groups
    ):
        """This class represents a quadrant in the physical maze which can be visited by the mouse

        Parameters
        ----------
        paths : str
            A string consisting of letters L,R,U,D specifying a direction in which a path exists to the next quadrant
        x : float
            the x position in cm of the box
        y : float
            the y position in cm of the box
        width : float
            the width in cm of the box
        height : float
            the height in cm of the box
        """
        self.LEFT = True
        self.RIGHT = True
        self.UP = True
        self.DOWN = True
        self.is_selected = False
        self.was_pressed = False
        self.hinted = False

        for c in paths:
            if c == "L":
                self.LEFT = False
            if c == "R":
                self.RIGHT = False
            if c == "U":
                self.UP = False
            if c == "D":
                self.DOWN = False

        super().__init__(x, y, width, height, *groups)



    def create_image(self, width, height, fac):
        if self.is_selected:
            self.fill_image(PASTEL_BLUE)
        elif self.is_hovered():
            self.fill_image(PASTEL_GREEN)
        elif self.hinted:
            self.fill_image(PASTEL_YELLOW)
        else:
            self.fill_image(PASTEL_APRICOT)
        color = PASTEL_BLACK
        if self.LEFT:
            self.draw_line((0, 0), (0, height - 1), color, 5)
        if self.RIGHT:
            self.draw_line((width - 1, 0), (width - 1, height - 1), color, 5)
        if self.UP:
            self.draw_line((0, 0), (width - 1, 0), color, 5)
        if self.DOWN:
            self.draw_line((0, height - 1), (width - 1, height - 1), color, 5)

        self.draw_circle((width / 2, height / 2), 3)

    @ScreenObject.modified_state
    def hint(self):
        self.hinted = True

    @ScreenObject.modified_state
    def unhint(self):
        self.hinted = False

    @ScreenObject.modified_state
    def select(self):
        self.is_selected = True

    @ScreenObject.modified_state
    def unselect(self):
        self.is_selected = False

    @ScreenObject.modified_state
    def process_events(self):
        if not self.was_pressed and self.is_hovered() and pg.mouse.get_pressed()[0]:
            self.select()
            self.was_pressed = True
        if not self.is_selected and self.was_pressed:
            if not pg.mouse.get_pressed()[0]:
                self.was_pressed = False
            self.unselect()


class PhysicalMaze(pg.sprite.Group):
    def __init__(self, map, physical_x_cm: float, physical_y_cm: float):
        super().__init__()
        self.x_cm = physical_x_cm
        self.y_cm = physical_y_cm

        self.num_y = len(map)
        self.num_x = len(map[0])
        self.box_width = self.x_cm / self.num_x
        self.box_height = self.y_cm / self.num_y

        self.builder_ref = MazeBuilder.from_paths_list(map)
        self.map: list[list[PhysicalBox]] = [
            [
                PhysicalBox(
                    paths,
                    x * self.box_width,
                    y * self.box_height,
                    self.box_width,
                    self.box_height,
                )
                for x, paths in enumerate(row)
            ]
            for y, row in enumerate(map)
        ]
        for row in self.map:
            for box in row:
                self.add(box)

    def get_distance(self, wx, wy, angle) -> float:
        """Get the distance from a given position (wx|wy) looking at a certain angle (0,90,180,360)

        Parameters
        ----------
        wx : _type_
            _description_
        wy : _type_
            _description_
        angle : _type_
            _description_

        Returns
        -------
        float
            _description_
        """
        current_box = None
        for row in self.map:
            for box in row:
                if box.rect.collidepoint(wx, wy):
                    current_box = box
        if current_box is None:
            return -1
        angle = angle % 360
        if angle == 0:
            return 1 if current_box.RIGHT else int(self.box_width)
        elif angle == 90:
            return 1 if current_box.UP else int(self.box_height)
        elif angle == 180:
            return 1 if current_box.LEFT else int(self.box_width)
        elif angle == 270:
            return 1 if current_box.DOWN else int(self.box_width)
        return -1

    def update_from_paths(self, walls: list[list[str]]):
        for y, row in enumerate(walls):
            for x, paths in enumerate(row):
                box = self.map[y][x]
                box.LEFT = True
                box.RIGHT = True
                box.UP = True
                box.DOWN = True
                for c in paths:
                    if c == "L":
                        box.LEFT = False
                    if c == "R":
                        box.RIGHT = False
                    if c == "U":
                        box.UP = False
                    if c == "D":
                        box.DOWN = False

    def update(self, *args: Any, **kwargs: Any) -> None:
        self.process_events()
        return super().update(*args, **kwargs)

    def process_events(self):
        selected = []
        for y, row in enumerate(self.map):
            for x, box in enumerate(row):
                if box.is_selected:
                    selected.append((x, y, box))
        if len(selected) > 1:
            x1, y1, box1 = selected[0]
            x2, y2, box2 = selected[1]
            # check adjacency
            if not (abs(x1 - x2) + abs(y1 - y2) == 1):
                for x, y, box in selected:
                    box.is_selected = False
                return
            # check if path exists
            edge_added = False
            if not self.builder_ref.has_edge(
                (x1, y1), (x2, y2)
            ) and not self.builder_ref.has_edge((x2, y2), (x1, y1)):
                self.builder_ref.edge((x1, y1), (x2, y2))
                edge_added = True
            if not edge_added:
                if self.builder_ref.has_edge((x1, y1), (x2, y2)):
                    self.builder_ref.remove_edge((x1, y1), (x2, y2))
                if self.builder_ref.has_edge((x2, y2), (x1, y1)):
                    self.builder_ref.remove_edge((x2, y2), (x1, y1))
            self.update_from_paths(self.builder_ref.to_wall_list())
            for x, y, box in selected:
                box.is_selected = False
