import sys

import numpy as np
import pygame as pg

from adapter.micro_mouse_adapter import MicroMouseAdapter
from constants import *
from maze.maze_builder import MazeBuilder
from maze.physical_maze import PhysicalMaze
from screen_objects import Camera, ScreenObject
from algorithm import Algorithm


class Painter:
    @staticmethod
    def drawRect(surface, pos: np.ndarray, size: np.ndarray, color: pg.Color = WHITE):
        pos = Camera.p2p(pos)
        size = Camera.p2s(size)
        pg.draw.rect(surface, color, [pos[0], pos[1], size[0], size[1]])

    @staticmethod
    def drawLine(
        surface, start: np.ndarray, end: np.ndarray, color: pg.Color = WHITE, width=1
    ):
        _start = tuple(Camera.p2p(start))
        _end = tuple(Camera.p2p(end))
        pg.draw.line(surface, color, _start, _end, width)

    @staticmethod
    def drawLineRelative(
        surface,
        start: np.ndarray,
        direction: np.ndarray,
        color: pg.Color = WHITE,
        width=1,
    ):
        Painter.drawLine(surface, start, start + direction, color, width)


class PygameMouse(MicroMouseAdapter, ScreenObject):
    def __init__(self, maze:PhysicalMaze, x: float, y: float, width: float, height: float, *groups
    ) -> None:
        MicroMouseAdapter.__init__(self)
        self.maze_ref = maze
        self.mouse_image = pg.image.load(IMAGE_PATH / "mouse.png")  # load image
        self.mouse_image = pg.transform.rotate(self.mouse_image, -90)
        self.set_color_key(BLACK)  # set black as transparent
        # rotation for mouse
        self.angle: float = 0
        self.was_pressed = False

        ScreenObject.__init__(self, x, y, width, height, *groups)

    def get_sensor(self, *direction: Direction):
        data: list[float] = []
        for d in direction:
            if d == Direction.FRONT:
                data.append(self.maze_ref.get_distance(self.wx, self.wy, self.angle))
            elif d == Direction.LEFT:
                data.append(self.maze_ref.get_distance(self.wx, self.wy, self.angle + 90)>2)
            elif d == Direction.RIGHT:
                data.append(self.maze_ref.get_distance(self.wx, self.wy, self.angle - 90)>2)
            elif d == Direction.BACK:
                data.append(self.maze_ref.get_distance(self.wx, self.wy, self.angle + 180))
        return data

    @ScreenObject.modified_state
    def move(self, num_blocks: int = 1):
        if self.get_sensor(Direction.FRONT)[0] > 2:
            self.x += num_blocks * np.cos(self.angle/180*np.pi) * self.maze_ref.box_width
            self.y -= num_blocks * np.sin(self.angle/180*np.pi) * self.maze_ref.box_height
        else:
            print("Error cannot move forward")
            raise Exception("Cannot move forward.")

    @ScreenObject.modified_state
    def rotate(self, degree: float):
        self.angle += degree

    def create_image(self, width, height, fac):
        self.fill_image(BLACK)
        self.draw_image(self.mouse_image)
        sensor_data = self.get_sensor(Direction.FRONT, Direction.LEFT, Direction.RIGHT, Direction.BACK)
        self.draw_line((width/2,height/2), (width/2+sensor_data[0]*fac,height/2), RED, 3)
        self.draw_line((width/2,height/2), (width/2,height/2-sensor_data[1]*fac), RED, 3)
        self.draw_line((width/2,height/2), (width/2,height/2+sensor_data[2]*fac), RED, 3)
        self.draw_line((width/2,height/2), (width/2-sensor_data[3]*fac,height/2), RED, 3)
        self.rotate_image(self.angle)

    def process_events(self):
        if not pg.key.get_pressed()[pg.K_w] and not pg.key.get_pressed()[pg.K_a] and not pg.key.get_pressed()[pg.K_d]:
            self.was_pressed = False
        if not self.was_pressed:
            if pg.key.get_pressed()[pg.K_w]:
                self.was_pressed = True
                self.move(1, 1)
            if pg.key.get_pressed()[pg.K_a]:
                self.was_pressed = True
                self.rotate(90, 1)
            if pg.key.get_pressed()[pg.K_d]:
                self.was_pressed = True
                self.rotate(-90, 1)
                
class World:
    def __init__(self, screen) -> None:
        size = sys.argv
        if len(size) > 1:
            mb = MazeBuilder(int(size[1]), int(size[1]))
        else:
            mb = MazeBuilder.load("live_edit.npy")
        map = mb.to_wall_list()
        self.screen = screen
        self.grid = PhysicalMaze(map, 200, 200)
        self.mouse = PygameMouse(self.grid, 0, 0, 15, 15)
        self.algo = Algorithm(self.mouse, mb.x, new_maze = int(input("Are we exploring a new maze? 0 for 'no, old maze' or 1 for 'yes, we need to explore!'\n")))
        self.algo.display = self.stupid_display
        self.last_time = pg.time.get_ticks()
        self.runCode = False
        
    def process_events(self):
        if pg.key.get_pressed()[pg.K_SPACE]:
            self.runCode = True

    def update(self):
        # Wait for input from user to finish building the maze
        self.process_events()
        # data = self.mouse.get_sensor(Direction.FRONT)
        self.grid.update()
        self.mouse.update()
        # Run algo slower than updates
        if pg.time.get_ticks() - self.last_time > 500:
            self.last_time = pg.time.get_ticks()
            if self.runCode and not self.algo.won:
                self.algo.run()

    def display(self):
        self.grid.draw(self.screen)
        self.mouse.draw(self.screen)

    def stupid_display(self):
        self.grid.draw(self.screen)
        self.mouse.draw(self.screen)
        pg.display.update()
        time.sleep(0.1)

    def save(self):
        self.grid.builder_ref.save("live_edit.npy")



if __name__ == "__main__":
    import time
    # pygame setup
    pg.init()
    screen = pg.display.set_mode(tuple(Camera.WINDOW_SIZE))
    clock = pg.time.Clock()
    Camera.move(91,91)
    world = World(screen)
    running = True
    dt = 0

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # RENDER YOUR GAME HERE
        screen.fill((255, 255, 255))
        world.update()
        world.display()
        # flip() the display to put your work on screen
        pg.display.update()

        clock.tick(60)  # limits FPS to 60

    world.save()
    pg.quit()
