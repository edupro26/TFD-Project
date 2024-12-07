from enum import Enum

class State(Enum):
    """
    Represents the possible states of a node
    """
    WAITING = 1
    RUNNING = 2
    RECOVERED = 3