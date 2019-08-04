import collections
import copy
from Objs.Items.SpecialItemBehavior import ITEM_INITIALIZERS, ITEM_COMBAT_ABILITY_CHANGES, ITEM_RESTRICTIONS, ITEM_EXTRA_ARGUMENTS

# I wonder if this needs to import Contestant...

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
            self.target = target  # The "Target" of the item, if any. Note that this will only ever be shallow copied, so be careful with dicts, etc.
            self.data = collections.OrderedDict()  # Note that this may be deepcopied, so be careful using this.
            if self.item.name not in ITEM_INITIALIZERS:
                return
            ITEM_INITIALIZERS[self.item.name](self)
    
    # Processes if the combat ability needs to change for this _particular_ combat (rather than in general)
    def RealTimeCombatAbilityChange(self, value, thisContestant, otherContestant):
        if self.item.name not in ITEM_COMBAT_ABILITY_CHANGES:
            return value
        return ITEM_COMBAT_ABILITY_CHANGES[self.item.name](self, value, thisContestant, otherContestant)

    @classmethod
    def copyOrMakeInstance(cls, item, count=1, target=None):
        if hasattr(item, "item"):
            newItem = copy.copy(item)
            newItem.data = copy.deepcopy(item.data)
        else:
            newItem = cls(item, count=count, target=target)
        return newItem

    @classmethod
    def takeOrMakeInstance(cls, item, count=1, target=None):
        if hasattr(item, "item"):
            newItem = item
        else:
            newItem = cls(item, count=count, target=target)
        return newItem

    def isInstanceOf(self, item):
        return (self.item == item)

    def __copy__(self):
        newInstance = type(self)(self.item, self.count, self.target)
        newInstance.data = self.data
        return newInstance

    def __deepcopy__(self, memo):
        newInstance = copy.copy(self)  # Might as well economize
        newInstance.data = copy.deepcopy(self.data, memo)
        return newInstance

    def __getattribute__(self, attr):
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
            object.__delattr__(self, attr, value)

    def __str__(self):  # we need another copy because __ methods completely bypass __getattribute__
        return self.name

    def onRemoval(self, contestant):
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
    inserted_callbacks = collections.OrderedDict()

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
                contestant.fullEventMultipliers[eventName][actorType] *= modifier
        for eventName, eventModifier in self.eventAdditions.items():
            for actorType, modifier in eventModifier.items():
                contestant.eventAdditions[eventName][actorType] += modifier
        for eventName, eventModifier in self.eventsDisabled.items():
            for actorType, modifier in eventModifier.items():
                contestant.eventDisabled[eventName][actorType] = modifier
            
    def makeInstance(self, count=1, data=None):
        if data is None:
            data = collections.OrderedDict()
        thisInstance = ItemInstance(self, count)
        thisInstance.data = data
        return thisInstance
