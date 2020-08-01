# this file is for defining enums for Meguca Arena
# in other files, import just the enums you need from this file

from enum import Enum
from typing import NamedTuple, Dict, Optional, Iterable, Type, Union
from Objs.Contestants.Contestant import Contestant
from Objs.Items.Item import Item, ItemInstance

# Used for managing expensive debugging functionality
class DebugMode(Enum):
    OFF = 0  # no debugging
    LOG = 1  # log messages when errors encountered
    EXCEPT = 2  # raise exception when error encountered
    
# TODO: Refactor the overall program to always return this named tuple? For now though, this is the preferred event output and standard tuples are deprecated.
Displayable = Union[Type[Item], Type[Contestant]]

class EventOutput(NamedTuple):
    description: str
    display_items: Optional[Iterable[Displayable]] = None
    dead: Optional[Iterable[str]] = None
    killer_dict: Optional[Dict[str, str]] = None  # Killed: Killer
    consumed_by_event_override: Optional[Iterable[Contestant]] = None  # Normally, contestants which are no longer valid for an event ia inferred from display_items. This overrides that.
    end_game_immediately: bool = False
    loot_table: Optional[Dict[str, Iterable[Type[Item]]]] = None
    injuries: Optional[Iterable[Contestant]] = None
    list_killers: bool = False  # If true, explicitly list killers for an event, based on killer_dict (often, this is unnecessary and implicit from the event itself.)
    no_contact: Optional[Iterable[Contestant]] = None  # For an event that makes contact, explicitly list contestants that don't (and hence don't spread disease)