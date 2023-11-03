from enum import Enum
from pathlib import Path
import numpy as np
import pygame as pg

#####################
#      Enums        #
#####################
class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    FRONT = 2
    BACK = 3
    
class Orientation(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class DirVec:
    LEFT = np.array([-1,0])
    RIGHT = np.array([1,0])
    UP = np.array([0,1])
    DOWN = np.array([0,-1])
    
class OrientVec:
    NORTH = np.array([-1,0])
    EAST = np.array([0,1])
    SOUTH = np.array([1,0])
    WEST = np.array([0,-1])

#####################
#     Variables     # 
#####################
PHY_DIST = 150

#####################
#      Colors        # Needs to be removed in the pi, because it does not support pygame
#####################

WHITE = pg.Color(255,255,255)
BLACK = pg.Color(0,0,0)
RED = pg.Color(255,0,0)
GREEN= pg.Color(0,255,0)
BLUE=pg.Color(0,0,255)
YELLOW=pg.Color(255,255,0)
CYAN=pg.Color(0,255,255)
MAGENTA=pg.Color(255,0,255)
PASTEL_RED = pg.Color(255, 102, 102)
PASTEL_GREEN = pg.Color(102, 255, 102)
PASTEL_BLUE = pg.Color(102, 102, 255)
PASTEL_YELLOW = pg.Color(255, 255, 102)
PASTEL_CYAN = pg.Color(102, 255, 255)
PASTEL_MAGENTA = pg.Color(255, 102, 255)
PASTEL_PURPLE = pg.Color(153, 102, 255)
PASTEL_ORANGE = pg.Color(255, 178, 102)
PASTEL_PINK = pg.Color(255, 102, 178)
PASTEL_LIME = pg.Color(178, 255, 102)
PASTEL_TEAL = pg.Color(102, 255, 178)
PASTEL_LAVENDER = pg.Color(178, 102, 255)
PASTEL_BROWN = pg.Color(153, 102, 102)
PASTEL_BEIGE = pg.Color(255, 255, 204)
PASTEL_MINT = pg.Color(204, 255, 255)
PASTEL_PEACH = pg.Color(255, 204, 255)
PASTEL_MAROON = pg.Color(102, 0, 51)
PASTEL_OLIVE = pg.Color(102, 102, 0)
PASTEL_APRICOT = pg.Color(255, 204, 153)
PASTEL_NAVY = pg.Color(0, 0, 102)
PASTEL_GREY = pg.Color(153, 153, 153)
PASTEL_BLACK = pg.Color(0, 0, 0)


#####################
#      Paths        #
#####################
IMAGE_PATH = Path(__name__).parent.absolute() / "res"
MAZE_PATH = Path(__name__).parent.absolute() / "mazes"
