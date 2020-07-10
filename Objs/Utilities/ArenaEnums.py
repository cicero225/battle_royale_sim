# this file is for defining enums for Meguca Arena
# in other files, import just the enums you need from this file

from enum import Enum

# Used for managing expensive debugging functionality
class DebugMode(Enum):
    OFF = 0  # no debugging
    LOG = 1  # log messages when errors encountered
    EXCEPT = 2  # raise exception when error encountered