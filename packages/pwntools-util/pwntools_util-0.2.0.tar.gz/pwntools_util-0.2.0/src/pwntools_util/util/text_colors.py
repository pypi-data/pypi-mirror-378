# ----- text colors -----

# imports

from enum import Enum

# constants

class TextColorCodes(Enum):
    Green = '\033[92m'
    Blue = '\033[94m'
    Yellow = '\033[93m'
    Reset = '\033[0m'

# functions

def colorize(text: str, color: TextColorCodes):
    return color.value + text + TextColorCodes.Reset.value
