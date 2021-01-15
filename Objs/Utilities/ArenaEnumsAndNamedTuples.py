# this file is for defining enums for Meguca Arena
# in other files, import just the enums you need from this file

# All the typing here leads to a lot of potential circular imports. THere is a great workaround for this, but it's convoluted and future, so we keep it confined here.
from __future__ import annotations
from typing import Any, NamedTuple, Dict, Optional, Iterable, Type, Union, Tuple, List, TYPE_CHECKING
if TYPE_CHECKING:
    from Objs.Contestants.Contestant import Contestant
    from Objs.Items.Item import Item, ItemInstance
    Displayable = Union[Type[Item], Type[Contestant]]

from enum import Enum

# Used for managing expensive debugging functionality
class DebugMode(Enum):
    OFF = 0  # no debugging
    LOG = 1  # log messages when errors encountered
    EXCEPT = 2  # raise exception when error encountered
    
# TODO: Refactor the overall program to always return this named tuple? For now though, this is the preferred event output and standard tuples are deprecated.

# The is is the output returned by events and parsed by the main and by HTMLWriter.addStructuredEvent
class EventOutput(NamedTuple):
    description: str
    display_items: Optional[Iterable[Displayable]]
    dead: Optional[Iterable[str]] = None
    killer_dict: Optional[Dict[str, str]] = None  # Killed: Killer
    consumed_by_event_override: Optional[Iterable[Contestant]] = None  # Normally, contestants which are no longer valid for an event ia inferred from display_items. This overrides that.
    end_game_immediately: bool = False
    loot_table: Optional[Dict[str, Iterable[Type[Item]]]] = None
    injuries: Optional[Iterable[Contestant]] = None
    list_killers: bool = False  # If true, explicitly list killers for an event, based on killer_dict (often, this is unnecessary and implicit from the event itself.)
    no_contact: Optional[Iterable[Contestant]] = None  # For an event that makes contact, explicitly list contestants that don't (and hence don't spread disease)
    destroyed_loot_table: Optional[List[str]] = None

class FightOutput(NamedTuple):
    description: str
    dead: Optional[Iterable[str]] = None
    killer_dict: Optional[Dict[str, str]] = None  # Killed: Killer
    loot_table: Optional[Dict[str, Iterable[Type[Item]]]] = None
    injuries: Optional[Iterable[Contestant]] = None
    destroyed_loot_table: Optional[List[str]] = None
   
# This is the class passed to the announcement queue that will be displayed after the the current event.
class EventAnnouncement(NamedTuple):
    description: str
    display_items: Iterable[Displayable]
    state: Any  # Maybe type this someday when state has a type
    preEventInjuries: Optional[Dict[str, bool]] = None
    block_if_any_contestant_dead: bool = True
    dead_here: Optional[Iterable[str]] = None # which characters in this event are known to be dead. Otherwise dead characters in display_items will be block the announcement if block_if_any_contestant_dead is True.

