from common import *

class Light:
    
    BASE_COLOR = Color(255, 255, 255)
    BASE_POSITION = Position(10, 10)
    BASE_SIZE = Size(0, 0)

    def __init__(self,position=BASE_POSITION) -> None:
        self.color = Light.BASE_COLOR
        self.position = position
        self.size = Light.BASE_SIZE







