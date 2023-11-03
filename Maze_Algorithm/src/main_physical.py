import sys
from time import sleep

from constants import *
from algorithm import Algorithm
from MicroMouseInterfacer import *
from adapter.micro_mouse_adapter import MicroMouseAdapter, FrontBlockedException

class PhysicalMouse(MicroMouseAdapter):
    def __init__(self) -> None:
        print("Physical Mouse initialized.")

    def get_sensor(self, *direction: list[Direction]):
        data = []
        for dir in direction:
            if dir == Direction.FRONT:
                print("reading FRONT")
                resp = read_sensor(Sensor.DISTANCE_FRONT)
                if resp[0]:
                    print(f"Success: {resp[1]}")
                    data.append(resp[1])
            elif dir ==  Direction.LEFT:
                print("reading LEFT")
                resp = read_sensor(Sensor.COLLISION_LEFT)
                if resp[0]:
                    data.append(resp[1])
                    print(f"Success: {resp[1]}")
            elif dir ==  Direction.RIGHT:
                print("reading RIGHT")
                resp = read_sensor(Sensor.COLLISION_RIGHT)
                if resp[0]:
                    data.append(resp[1])
                    print(f"Success: {resp[1]}")
            if resp != None and not resp[0]:
                raise Exception(f"Failed to read sensor of {direction}")
        return data

    def rotate(self, degree: float, speed: float):
        # Error correction for hardwaare
        offset = 240
        if degree > -1:
            turn_left(int((offset+degree)/90))
        else:
            turn_right(int(-(degree-offset)/90))

    def move(self, num_blocks : int = 1):
        # Error correction for hardwaare
        offset = 2
        resp = read_sensor(Sensor.DISTANCE_FRONT)
        # print(f"move() front distance: {resp[1]}")
        if resp[0] and resp[1] > PHY_DIST:
            move_forward(num_blocks*offset)
        else:
            raise FrontBlockedException()
    
    def move_backwards(self, num_blocks : int = 1):
        move_backwards(num_blocks)

if __name__ == "__main__":
    op_mode = input('What operation mode are we accessing? Maze solver (press 0) or a remote control (press 1)?\n')
    while not (op_mode == "0" or op_mode == "1"):
        op_mode = input("Please choose eihter 0 or 1\n")
    op_mode = int(op_mode)
    mouse = PhysicalMouse()
    if op_mode:
        while(True):
            key = input("Enter W to move forward, A and D to rotate and S to move backward.\nThen add an :[number] to signalize how much rotation/movement you desire!\n")
            if "escape" in key.lower():
                print("Exiting")
                break;
            key = key.split(":")
            mov = key[0].strip()
            nr = int(key[1].strip())
            if mov == 'w':
                print(f"Moving FRONT by {nr}")
                try:
                    mouse.move(nr)
                except:
                    print("Front is blocked! Can't move :(")
            elif mov == 'a':
                print(f"Rotating by {nr} degrees to the LEFT")
                mouse.rotate(nr)
            elif mov == 'd':
                print(f"Rotating by {nr} degrees to the RIGHT")
                mouse.rotate(-nr)
            elif mov == 's':
                print(f"Moving BACK by {nr}!")
                mouse.move_backwards(nr)
    else:
        new_maze = int(input("Are we exploring a new maze? 0 for 'no, old maze' or 1 for 'yes, we need to explore!'\n"))
        size = sys.argv
        if len(size) > 1:
            algorihtm = Algorithm(mouse, int(size[1]), new_maze=new_maze, avrg_dist=PHY_DIST)
            if len(size) > 3:
                algorihtm = Algorithm(mouse, int(size[1]), new_maze=new_maze, orientation=Orientation(int(size[2])), avrg_dist=PHY_DIST)
        else:
            algorihtm = Algorithm(mouse, 11, new_maze=new_maze, avrg_dist=PHY_DIST)
            
        while(not algorihtm.won):
            # sleep(2)
            input("Ready?")
            algorihtm.run()