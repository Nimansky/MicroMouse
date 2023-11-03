from typing_extensions import Self
from time import sleep
from ast import literal_eval

from constants import *
from adapter.micro_mouse_adapter import MicroMouseAdapter, FrontBlockedException

class Tile:
    def __init__(self) -> None:
        self.north: Self = None
        self.east: Self = None
        self.south: Self = None
        self.west: Self = None
        
        self.flood_nr = None
        
    def set_orientation(self, orientation: Orientation, val):
        """Sets the value for the given orientation in the value accordingly.

        Parameters
        ----------
        orientation : Orientation
            The Orientation that needs to be set for this Tile
        val : Tile
            The Tile the orientation variable should be set to
        """
        if orientation == Orientation.NORTH:
            self.north = val
        if orientation == Orientation.EAST:
            self.east = val
        if orientation == Orientation.SOUTH:
            self.south = val
        if orientation == Orientation.WEST:
            self.west = val
            
    def get_orientation(self) -> list[Self]:
        """Returns the orientation variables in a list.

        Returns
        -------
        list
            List of the orientaiton variables.
        """
        return [self.north, self.east, self.south, self.west]

class Algorithm:
    def __init__(self, mouse: MicroMouseAdapter, size: int, avrg_dist:int = 2, goal: tuple = None, new_maze: bool = True, orientation: Orientation = Orientation.EAST) -> None:
        # Changeable, if goal somewhere else than the middle
        self.won = False
        self.avrg_dist = avrg_dist
        if goal:
            self.goal = goal
        else:
            self.goal = (int(size/2), int(size/2))
        self.mouse = mouse
        self.last_was_right = False
        self.backtrack = False
        self.position = np.array([0,0])
        # Array of Orientation -> Path we have traveled so far
        self.path = []
        # Append the indice of the path, so the mouse can backtrack the unvisited Tiles, if there's no more Path in the current run
        # Remove indice, if we happen to visit the Tile anyway (it means we have loop), once visited, check for new paths, if there are no new paths -> Backtrack!
        
        # Format: { [indice]: [pos_x, pos_y] }
        self.unvisited = {}
        self.mouse_orient = orientation
        
        # Load Tile_Matrix if we explored already
        if new_maze:
            self.tile_matrix: list[list[Tile]] = [[None for _ in range(size)] for _ in range(size)]
        else:
            self.tile_matrix = np.load(MAZE_PATH/ "explored_maze.npy", allow_pickle=True)
        
        # Init the first Tile
        if not self.tile_matrix[self.position[0]][self.position[1]]:
            self.tile_matrix[self.position[0]][self.position[1]] = Tile()
    
    # Make the mouse move into a certain direction, only one field!
    def move(self, orientation: Orientation = None, num_blocks: int = 1):
        # Rotate accordingly, then move, if no orientation given, just move forward.
        if not orientation:
            orientation = self.mouse_orient
        else:
            self.rotate(((self.mouse_orient.value - orientation.value) % 4) * 90)
            if self.avrg_dist > 2:
                input('Ready?')
            self.display()
        
        try:
            self.mouse.move(num_blocks)
            if self.avrg_dist > 2:
                sleep(1)
            self.display()
        except FrontBlockedException:
            return
        # Change current position accordigly
        self.position = self.map_orientation_with_vector(orientation, self.position)
        # TODO: Now think about, whether we want to add to path ALL the time? When backtracking too? 
        # Lastly add last step into the path
        self.path.append(orientation)
        self.last_was_right = False
    
    # Rotate function that can handle 270 degrees -> Inversed degrees 90 left, -90 right
    def rotate(self, degree: float):
        orientation = self.mouse_orient.value
        if degree == 90 or degree == -270:
            orientation -= 1
            self.mouse.rotate(90)
        elif degree == -90 or degree == 270:
            orientation += 1
            self.mouse.rotate(-90)
        elif np.abs(degree) == 180:
            orientation += 2
            # We simply rotate twice by 90 degree if we want to turn around
            self.mouse.rotate(90)
            self.display()
            self.mouse.rotate(90)
        self.mouse_orient = Orientation(orientation % 4)
        
    def map_orientation_with_vector(self, orientation: Orientation, matrix_pos: np.array) -> np.array:
        """A helper function that adds the correct matrix values to 2D-array and retunrs the new position

        Parameters
        ----------
        orientation : Orientation
            The Orientation value that needs to be matched, in order to add the correct Orientation Vector to the matrix_pos value
        matrix_pos : np.array
            A 2D-Array that represents a position inside the matrix

        Returns
        -------
        np.array
            The new position in relation to the old matrix_pos one into the direction of the orientation
        """
        new_val = np.array([i for i in matrix_pos])
        if orientation == Orientation.NORTH:
            new_val += OrientVec.NORTH
        elif orientation == Orientation.EAST:
            new_val += OrientVec.EAST
        elif orientation == Orientation.SOUTH:
            new_val += OrientVec.SOUTH
        elif orientation == Orientation.WEST:
            new_val += OrientVec.WEST
        return new_val
    
    def get_position(self, direction: Direction) -> np.array:
        """Gets the position in the direciton wanted of the mouse in relation to the self.position variable.
        This method is useful for getting the indices for the values in the matrix.

        Parameters
        ----------
        direction : Direction
            In which direction we need to position from

        Returns
        -------
        np.array
            The position either left, right, front, or back from the mouse
        """
        pos = np.array([])
        if direction == Direction.RIGHT:
            # Depending on the resulting orientation, add the Orientation value to the position accordingly
            pos = self.map_orientation_with_vector(Orientation((self.mouse_orient.value + 1) % 4), self.position)
        elif direction == Direction.LEFT:
            pos = self.map_orientation_with_vector(Orientation((self.mouse_orient.value - 1) % 4), self.position)
        elif direction == Direction.BACK:
            pos = self.map_orientation_with_vector(Orientation((self.mouse_orient.value + 2) % 4), self.position)
        elif direction == Direction.FRONT:
            pos = self.map_orientation_with_vector(self.mouse_orient, self.position)
        return pos
    
    def run(self):
        # Generally we only move, if we have not visited that Tile
        # If the left side is free, jsut add a Tile in the matrix and make the connection, then mark as unvisited
        # If we can only go left, we will rotate, and then Tile is in the front
        try:
            left_sense = self.mouse.get_sensor(Direction.LEFT)
        except:
            print("Could not sense left sensor!")
            return
        if left_sense[0]:
            left_pos = self.get_position(Direction.LEFT)
            if not self.tile_matrix[left_pos[0]][left_pos[1]]:
                new_LTile = Tile()
                new_LTile.set_orientation(Orientation((self.mouse_orient.value + 1) % 4), self.tile_matrix[self.position[0]][self.position[1]])
                self.tile_matrix[left_pos[0]][left_pos[1]] = new_LTile
                self.tile_matrix[self.position[0]][self.position[1]].set_orientation(Orientation((self.mouse_orient.value - 1) % 4), self.tile_matrix[left_pos[0]][left_pos[1]])
                self.unvisited[str(left_pos.tolist())] = len(self.path)
        # action has already been chosen? We have to act differently in each if-condition, depending whether there has been an aciotn or not
        action = False
        # If our current position is not initialized with a tile yet, then 
        # First check each time, if there is a path on the right! We follow the wall to explore
        ## Several options for an empty right path:
        # 1. We have never visited the right side (Matrix on that position empty)
        # 2. We have seen the right side before (it is initialized), but never visited -> Check self.unvisisted
        # 3. We have visited the right side -> Then we check forward and lastly left!
        try:
            right_sense = self.mouse.get_sensor(Direction.RIGHT)
        except:
            print("Could not sense right sensor!")
            return
        if not self.last_was_right and right_sense[0]:
            right_pos = self.get_position(Direction.RIGHT)
            # Case 1: Never seen nor visited!
            if not self.tile_matrix[right_pos[0]][right_pos[1]]:
                new_RTile = Tile()
                new_RTile.set_orientation(Orientation((self.mouse_orient.value - 1) % 4), self.tile_matrix[self.position[0]][self.position[1]])
                self.tile_matrix[right_pos[0]][right_pos[1]] = new_RTile
                self.tile_matrix[self.position[0]][self.position[1]].set_orientation(Orientation((self.mouse_orient.value + 1) % 4), self.tile_matrix[right_pos[0]][right_pos[1]])
                self.rotate(-90)
                self.last_was_right = True
                action = True
            # Case 2: "Seen"! Never visited!
            elif any([np.array_equal(right_pos, val) for val in [literal_eval(i) for i in self.unvisited.keys()]]):
            # elif self.backtrack:
                # If the node on the right, was one of the "seen" ones, add a link between the current position and the right to it
                self.tile_matrix[self.position[0]][self.position[1]].set_orientation(Orientation((self.mouse_orient.value + 1) % 4), self.tile_matrix[right_pos[0]][right_pos[1]])
                self.tile_matrix[right_pos[0]][right_pos[1]].set_orientation(Orientation((self.mouse_orient.value - 1) % 4), self.tile_matrix[self.position[0]][self.position[1]])
                self.rotate(-90)
                self.last_was_right = True
                action = True
                # Now we remove the mark from the self.unvisited dict!
                # self.unvisited = {k:v for k,v in self.unvisited if v!=right_pos}-> NO, cannot remove yet, since we have NOT visited yet!! Only rotated!!              
        ## Case right is blocked: We move forward if possible!
        # Options:
        # 1. Right side is not free, thus we have to move forward (if free), Tile does NOT exist yet!
        # 2. We just turned, and front is free now, Tile exists!
        try:
            front_sense = self.mouse.get_sensor(Direction.FRONT)
        except:
            print("Could not sense front sensor!")
            return
        if front_sense[0] > self.avrg_dist:
            # This means the Tile exists already
            front_pos = self.get_position(Direction.FRONT)
            if self.last_was_right and not action:
                self.move()
                self.last_was_right = False
                action = True
                if any([np.array_equal(front_pos, val) for val in [literal_eval(i) for i in self.unvisited.keys()]]):
                    del self.unvisited[str(front_pos.tolist())]
            # We're just moving forward, we didn't turn and Tile does not exist
            # NOTE: It's not possible to have an aciton not NOT turned right beforehand -> Since that is the only action that could happen beforehand
            else:
                # Case: We have never seen the FRONT Tile
                if not self.tile_matrix[front_pos[0]][front_pos[1]]:
                    front_Tile = Tile()
                    front_Tile.set_orientation(Orientation((self.mouse_orient.value - 2) % 4), self.tile_matrix[self.position[0]][self.position[1]])
                    # First set the val in the matrix
                    self.tile_matrix[front_pos[0]][front_pos[1]] = front_Tile
                    # Then let our matrix value point at the other matrix value and not the floating variable in this scope
                    self.tile_matrix[self.position[0]][self.position[1]].set_orientation(self.mouse_orient, self.tile_matrix[front_pos[0]][front_pos[1]])
                    self.move()
                    self.last_was_right = False
                    action = True
                # Case: We've seen the FRONT Tile before! Did we visit it too?
                elif not action and (self.backtrack or any([np.array_equal(front_pos, val) for val in [literal_eval(i) for i in self.unvisited.keys()]])):
                    self.backtrack = False
                    self.tile_matrix[self.position[0]][self.position[1]].set_orientation(self.mouse_orient, self.tile_matrix[front_pos[0]][front_pos[1]])
                    self.tile_matrix[front_pos[0]][front_pos[1]].set_orientation(Orientation((self.mouse_orient.value - 2) % 4), self.tile_matrix[self.position[0]][self.position[1]])
                    self.move()
                    self.last_was_right = False
                    action = True
                    # self.unvisited = {k:v for k,v in self.unvisited.items() if not np.array_equal(v,front_pos) }
                    if any([np.array_equal(front_pos, val) for val in [literal_eval(i) for i in self.unvisited.keys()]]):
                        del self.unvisited[str(front_pos.tolist())]
        # Now think about whether we want the sensor values ANEW or get ones from before for the LEFT case? Maybe sense both ways and create Tiles first, then check where to go?
        if not action:
            ## If we reach this state, there are no ways FRONT and RIGHT, therefore since we add all LEFT paths to self.unvisited anyway
            # We just backtrack the last self.unvisited node
            if len(self.unvisited) > 0:
                self.backtrack = True
                ## TODO: Why does a yield pop ANOTHER value???
                unv_pos, back_index = self.unvisited.popitem()
                self.unvisited[unv_pos] = back_index
                unv_pos = literal_eval(unv_pos)
                if back_index == len(self.path):
                    self.rotate(90)
                    self.last_was_right = False
                    action = True
                    self.backtrack = False
                else:
                    way_back = self.path[back_index:]
                    way_back = [way_back[i] for i in range(len(way_back)-1, -1, -1)]
                    for b_orientation in way_back:
                        if np.array_equal(self.position, unv_pos):
                            break
                        self.move(Orientation((b_orientation.value + 2) % 4))
                    # Since we're back at the position before, we simply cut off the deadend path
                    self.path = self.path[:back_index]
                    self.last_was_right = False
                    # continue
            # Conditions met: No actions happened, nor are there unvisited nodes
            # Now Floodfill the start and goal! No need for while-Loop anymore
            elif self.won == False:
                if not np.array_equal(self.position, [0,0]):
                    self.floodfill((0,0))
                    self.follow_flood()
                    self.reset_flood_nr()
                self.solve_maze()
            ## NOTE: If no action taken so far, we are either Dead End or only can turn left, therefore we check for unvisited nodes, since we add left nodes at the beginning
            # Then we either visit LEFT or we backtrack to the location, where we have not yet visited
            # After reaching that position, we move towards it, and scan the neighbours again
            # We fill up the matrix and self.unvisited in the beginning of the iteration if LEFT is free
            # Sense whether there's space on the LEFT _before_ any action -> Like this we will check LEFT side on each iteration, even after rotation since it counts as an action
            
    def solve_maze(self):
        val = self.floodfill(self.goal)
        if val == -1:
            return
        self.follow_flood()
        self.won = True
        np.save(MAZE_PATH/ "explored_maze.npy", self.tile_matrix, allow_pickle=True)
            
    def follow_flood(self):
        curr_Tile: Tile = self.tile_matrix[self.position[0]][self.position[1]]
        while(curr_Tile != None and curr_Tile.flood_nr != 0):
            neighbors = curr_Tile.get_orientation()
            lowest_Tile: list[int|Tile] = [[i, pre_neigh] for i, pre_neigh in enumerate(neighbors) if pre_neigh != None]
            if len(lowest_Tile) > 0:
                lowest_Tile = lowest_Tile[0]
            else:
                return
            for i, neigh in enumerate(neighbors):
                if neigh != None and neigh.flood_nr < lowest_Tile[1].flood_nr:
                    lowest_Tile = [i, neigh]
            if lowest_Tile[0] == 0:
                self.move(Orientation.NORTH)
            elif lowest_Tile[0] == 1:
                self.move(Orientation.EAST)
            elif lowest_Tile[0] == 2:
                self.move(Orientation.SOUTH)
            elif lowest_Tile[0] == 3:
                self.move(Orientation.WEST)
            curr_Tile: Tile = self.tile_matrix[self.position[0]][self.position[1]]
            
            
    def floodfill(self, goal: tuple, water_lvl = 0) -> None:
        """Fills up the flood_nr in each Tile of the matrix

        Parameters
        ----------
        goal : tuple
            The Tile which flood_nr needs to be set
        """
        goal_Tile: Tile = self.tile_matrix[goal[0]][goal[1]]
        if goal_Tile == None:
            if water_lvl == 0:
                print("Impossible to solve the maze!")
                return -1
            return
        if goal_Tile.flood_nr == None or goal_Tile.flood_nr > water_lvl:
            goal_Tile.flood_nr = water_lvl
        else:
            return
        
        for neigh in goal_Tile.get_orientation():
            if neigh:
                self.floodfill(self.find_TilePos(neigh), water_lvl+1)
            
    def find_TilePos(self, elem: Tile) -> tuple:
        """Find the position of the Tile inside the matrix.

        Parameters
        ----------
        elem : Tile
            The Tile that needs to be found

        Returns
        -------
        tuple
            The indices of the Tile as a tuple
        """
        for i in range(len(self.tile_matrix)):
            for j in range(len(self.tile_matrix[i])):
                if self.tile_matrix[i][j] == elem:
                    return (i, j)
    
    def reset_flood_nr(self) -> None:
        """Sets all flood numbers of the tile_matrix to None
        """
        for row in self.tile_matrix:
            for tile in row:
                if tile != None:
                    tile.flood_nr = None
    
    def display(self):
        pass