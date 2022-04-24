import collections
import copy
from Objs.Items.SpecialItemBehavior import ITEM_INITIALIZERS, ITEM_COMBAT_ABILITY_CHANGES, ITEM_RESTRICTIONS, ITEM_EXTRA_ARGUMENTS, ITEM_ON_ACQUISITION, ITEM_ON_REMOVAL, ITEM_DISPLAY_OVERRIDE, ITEM_IMAGE_DISPLAY_OVERRIDE

from typing import Dict, Callable
# stats stack, other things don't, at the moment

class InstanceInsteadOfMainThing(Exception):
    pass


class ItemInstanceWithoutIternalItem(Exception):
    pass


class ItemInstance(object):

    stateStore = [None]

    def __init__(self, item, count=1, target=None):
        if hasattr(item, "item"):
            raise InstanceInsteadOfMainThing
        else:
            self.item = item
            self.count = count
            self.owner = None  # The owner is responsible for keeping this updated, using onAcquisition (NOT direct setting)
            self.target = target  # The "Target" of the item, if any. Note that this will only ever be shallow copied, so be careful with dicts, etc.
            self.eventHandlers = {}  # This _will_ be deepcopied along with the item.
            self.data = collections.OrderedDict()  # Note that this may be deepcopied, so be careful using this.
            if self.item.name not in ITEM_INITIALIZERS:
                return
            ITEM_INITIALIZERS[self.item.name](self)
    
    # Note that this is not same in the sense of being the same item, having the same handlers, etc., which could be done with id(item).
    # This is just a rough check that it is the "same" item in a gameplay sense.
    def is_same_item(self, other, strict=False, ignore_count=True, ):
        if strict and not isinstance(other, ItemInstance):
            raise "Illegal strict ItemInstance comparison."
        # We allow "other" to be a string for convenience. In that case the only possible meaning is a simple name check.
        if isinstance(other, str):
            return self.name == other         
        if isinstance(other, Item):
            if not ignore_count and (self.count != 1):
                return False
            return self.name == str(other)
        return (self.name == other.name) and (self.target == other.target) and (ignore_count or (self.count == other.count))        
    
    # Processes if the combat ability needs to change for this _particular_ combat (rather than in general)
    def RealTimeCombatAbilityChange(self, value, thisContestant, otherContestant):
        if self.item.name not in ITEM_COMBAT_ABILITY_CHANGES:
            return value
        return ITEM_COMBAT_ABILITY_CHANGES[self.item.name](self, value, thisContestant, otherContestant)

    @classmethod
    def copyOrMakeInstance(cls, item, count=None, target=None):
        if isinstance(item, ItemInstance):
            if count is not None and count != item.count:
                raise Exception("Attempt to take stackable item with incorrect count")
            newItem = copy.copy(item)
            newItem.data = copy.deepcopy(item.data)
            newItem.eventHandlers = copy.deepcopy(item.eventHandlers)
        else:
            newItem = cls(item, count=count, target=target)
        return newItem

    # Note: if split_stackable is true the item is _never_ taken by reference, since the behavior
    # would otherwise be inconsistent depending on if we're taking the whole stack or not. This
    # leaves a residual item with count=0, which it is the caller's responsibility to destroy.
    @classmethod
    def takeOrMakeInstance(cls, item, count=1, target=None, split_stackable=False):
        if isinstance(item, ItemInstance):
            if count == item.count:
                if split_stackable:
                    item.count -= count
                    return cls(item.item, count=count, target=item.target)
                newItem = item
            else:
                if not split_stackable:
                    raise Exception("Attempt to take stackable item with incorrect count")
                else:
                    item.count -= count
                    return cls(item.item, count=count, target=item.target)
        else:
            newItem = cls(item, count=count, target=target)
        return newItem

    def isInstanceOf(self, item):
        return (self.item == item)

    def __copy__(self):
        newInstance = type(self)(self.item, self.count, self.target)
        newInstance.data = self.data
        newInstance.eventHandlers = self.eventHandlers
        return newInstance

    def __deepcopy__(self, memo):
        newInstance = copy.copy(self)  # Might as well economize
        newInstance.data = copy.deepcopy(self.data, memo)
        newInstance.eventHandlers = copy.deepcopy(self.eventHandlers, memo)
        return newInstance

    # TODO: maybe just rename things so it has a proper internal and external friendly?
    def friendly_processor(self):
        special_display = ITEM_DISPLAY_OVERRIDE.get(self.item.name)
        if special_display is None:
            return None
        return special_display(self, self.owner, self.stateStore[0])
        
    def image_file_processor(self):
        special_display = ITEM_IMAGE_DISPLAY_OVERRIDE.get(self.item.name)
        if special_display is None:
            return None
        return special_display(self, self.owner, self.stateStore[0])

    def __getattribute__(self, attr):
        if attr == "friendly":
            try_special = self.friendly_processor()
            if try_special is not None:
                return try_special
        elif attr == "imageFile":
            try_special = self.image_file_processor()
            if try_special is not None:
                return try_special
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return getattr(object.__getattribute__(self, "item"), attr)

    def __setattr__(self, attr, value):
        if attr == "item" and not hasattr(self, "item"):
            object.__setattr__(self, attr, value)
            return
        # Unique exception, allowing friendly to be overridden for item instances.
        if attr == "friendly":
            object.__setattr__(self, attr, value)
            return
        if hasattr(self.item, attr):
            setattr(self.item, attr, value)
        else:
            object.__setattr__(self, attr, value)

    def __delattr__(self, attr):
        if hasattr(self.item, attr):
            self.item.__delattr__(attr)
        else:
            object.__delattr__(self, attr)

    def __str__(self):  # we need another copy because __ methods completely bypass __getattribute__
        return self.name

    def onAcquisition(self, contestant, resetItemAllowed=False):
        self.item.onAcquisition(contestant, resetItemAllowed)
        self.owner = contestant
        if self.item.name not in ITEM_ON_ACQUISITION:
            return
        ITEM_ON_ACQUISITION[self.item.name](self, contestant, self.stateStore[0])

    def onRemoval(self, contestant):
        self.owner = None
        if self.item.name not in ITEM_ON_REMOVAL:
            return
        ITEM_ON_REMOVAL[self.item.name](self, contestant, self.stateStore[0])
        pass

    # this has to be processed before anything else...
    def applyObjectStatChanges(self, contestant):
        for changedStat in self.statChanges:
            contestant.stats[changedStat] = max(min(
                contestant.stats[changedStat] + self.statChanges[changedStat] * self.count, 10), 0)
                
    def checkItemValidity(self, contestant, isNew, resetItemAllowed=False):
        itemCallback = ITEM_RESTRICTIONS.get(self.item.name)
        return itemCallback is None or itemCallback(self, contestant, isNew, resetItemAllowed)
    
    def parseExtraArguments(self, extraArguments):
        itemCallback = ITEM_EXTRA_ARGUMENTS.get(self.item.name)
        return itemCallback is None or itemCallback(self, extraArguments)

class Item(object):

    # Some events need to place callbacks in main. Place here at import time. key -> callback location, value-> callback
    inserted_callbacks: Dict[str, Callable] = collections.OrderedDict()

    def __init__(self, name, inDict, settings):
        # The item class has certain stereotyped effects on characters that can be encoded in json
        self.name = name
        self.friendly = inDict["friendly"] if "friendly" in inDict else self.name
        self.imageFile = inDict["imageFile"]
        self.settings = settings
        # This dict (string:int) stores any direct additions/subtractions in stats given by the Item
        self.statChanges = inDict["statChanges"]
        # This dict (string: dict(string: float) stores any event multiplier effects given by the object. Keys are events, followed by main/participant/victim
        self.eventMultipliers = inDict["eventMultipliers"]
        # This dict (string: dict(string: float)) stores any event additive effects given by the object. Keys are events, followed by main/participant/victim
        self.eventAdditions = inDict["eventAdditions"]
        # This dict (string: bool) stores any events actively disabled by this object. Keys are events, followed by main/participant/victim. If you don't want a subcategory disabled, you can not include a listing, or explicitly have a boolean
        self.eventsDisabled = inDict["eventsDisabled"]
        self.stackable = inDict["stackable"]
        self.distinct = inDict.get("distinct", False)
        self.lootable = inDict.get("lootable", True)  # defaults to True.
        if settings["objectInfluence"] != 1:
            self.applyObjectInfluence(self.statChanges)
            self.applyObjectInfluence(self.eventMultipliers)
            self.applyObjectInfluence(self.eventAdditions)
        self.rawData = inDict

    def __str__(self):
        return self.name

    @classmethod
    def registerInsertedCallback(cls, callbackLocation, callback):
        cls.inserted_callbacks.setdefault(
            callbackLocation, []).append(callback)
    
    # Convenience methods for common item tasks
    @classmethod
    def registerPostPhaseCallback(cls, callback):
        cls.registerInsertedCallback("postPhaseCallbacks", callback)

    def applyObjectInfluence(self, inDict):
        for key in inDict:
            inDict[key] *= self.settings["objectInfluence"]

    def onAcquisition(self, contestant, resetItemAllowed=False):
        for eventName, eventModifier in self.eventMultipliers.items():
            for actorType, modifier in eventModifier.items():
                contestant.fullEventMultipliers[eventName].setdefault(actorType, 1)
                contestant.fullEventMultipliers[eventName][actorType] *= modifier
        for eventName, eventModifier in self.eventAdditions.items():
            for actorType, modifier in eventModifier.items():
                contestant.eventAdditions[eventName].setdefault(actorType, 1)
                contestant.eventAdditions[eventName][actorType] += modifier
        for eventName, eventModifier in self.eventsDisabled.items():
            for actorType, modifier in eventModifier.items():
                contestant.eventDisabled[eventName].setdefault(actorType, False)
                contestant.eventDisabled[eventName][actorType] = modifier
            
    def makeInstance(self, count=1, data=None):
        if data is None:
            data = collections.OrderedDict()
        thisInstance = ItemInstance(self, count)
        thisInstance.data = data
        return thisInstance
    
    # Note that this is not same in the sense of being the same item, having the same handlers, etc., which could be done with id(item).
    # This is just a rough check that it is the "same" item in a gameplay sense.
    # ignore_count is provided to match the 
    def is_same_item(self, other, strict=False):
        if strict and not isinstance(other, Item):
            raise "Illegal strict Item comparison."
        # We allow "other" to be a string for convenience. In that case the only possible meaning is a simple name check.   
        return self.name == str(other)
            
