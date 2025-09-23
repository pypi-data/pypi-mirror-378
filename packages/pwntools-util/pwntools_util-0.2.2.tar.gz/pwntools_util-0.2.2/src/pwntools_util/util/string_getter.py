# ----- string getter -----

# imports

from enum import Enum

import re

# constants

class Patterns(Enum):
    INTEGER = r"[+-]?\d+"
    FLOAT = r"[+-]?(?:\d+\.\d+|\d+\.?|\.\d+)(?:[Ee][+-]?\d+)?"
    UNNESTED_LIST_CONTENT = r"\[(.+)\]"

# simple regex functions

def getAllFromString(string: str, pattern: str):
    return tuple(re.findall(pattern, string))

def getFromString(string: str, pattern: str):
    return re.search(pattern, string)[0]

def getSimpleListFromString(string: str, separator: str = None):
    return re.search(Patterns.UNNESTED_LIST_CONTENT.value, string)[1].split(separator)

# integer functions

def getFromString_Int(string: str):
    return int(getFromString(string, Patterns.INTEGER.value))

def getAllFromString_Int(string: str):
    return tuple(int(s) for s in getAllFromString(string, Patterns.INTEGER.value))

def toList_Int(a_list: list[str]):
    return [getFromString_Int(x) for x in a_list]

def getListFromString_Int(string: str):
    return toList_Int(getSimpleListFromString(string))

# float functions

def getFromString_Float(string: str):
    return float(getFromString(string, Patterns.FLOAT.value))

def getAllFromString_Float(string: str):
    return tuple(float(s) for s in getAllFromString(string, Patterns.FLOAT.value))

def toList_Float(a_list: list[str]):
    return [getFromString_Float(x) for x in a_list]

def getListFromString_Float(string: str):
    return toList_Float(getSimpleListFromString(string))
