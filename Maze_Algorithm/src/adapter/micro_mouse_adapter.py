from constants import Direction

class MicroMouseAdapter:
    def __init__(self) -> None:
        pass

    def get_sensor(self, *direction: list[Direction]):
        raise NotImplementedError

    def rotate(self, degree: float, speed: float):
        raise NotImplementedError
        
    def move(self, num_blocks : int):
        raise NotImplementedError
    
class FrontBlockedException(Exception):
    "Our FRONT is blocked."