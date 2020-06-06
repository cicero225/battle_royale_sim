"""stats should vary from 0-10. 5 is average and will not affect any events."""

# In case of Python 2+. The Python 3 implementation is way less dumb.
from __future__ import division
from Objs.Items.Item import ItemInstance
from Objs.Items.Status import StatusInstance
import Objs.Utilities.ArenaUtils as ArenaUtils

import random
import collections


def contestantIndivActorCallback(actor, baseEventActorWeight, event):
    try:  # Pythonic, etc. Really, it's preferred this way...
        if actor.eventDisabled[event.name]["main"]:
            return (0, False)
    except KeyError:
        pass

    try:
        addition = actor.eventAdditions[event.name]["main"]
    except KeyError:
        addition = 0

    try:
        multiplier = actor.fullEventMultipliers[event.name]["main"]
    except KeyError:
        multiplier = 1
    # Base single event probability
    return (baseEventActorWeight * multiplier + addition, True)


def contestantIndivActorWithParticipantsCallback(_, participant, baseEventParticipantWeight, event):
    try:
        addition = participant.eventAdditions[event.name]["participant"]
    except KeyError:
        addition = 0

    try:
        multiplier = participant.fullEventMultipliers[event.name]["participant"]
    except KeyError:
        multiplier = 1
    return (baseEventParticipantWeight * multiplier + addition, True)


def contestantIndivActorWithVictimsCallback(_, victim, baseEventVictimWeight, event):
    try:
        addition = victim.eventAdditions[event.name]["victim"]
    except KeyError:
        addition = 0

    try:
        multiplier = victim.fullEventMultipliers[event.name]["victim"]
    except KeyError:
        multiplier = 1
    return (baseEventVictimWeight * multiplier + addition, True)


class Contestant(object):

    stateStore = [None]
    onDeathCallbacks = []

    # In this case, best to bake the stats as its own thing in the json...
    def __init__(self, name, inDict, settings):
        self.name = name
        self.gender = inDict['gender']
        self.imageFile = inDict['imageFile']
        self.stats = inDict['stats']
        self.inventory = []
        self.statuses = []
        self.settings = settings
        if not self.settings["statNormalization"]:
            self.contestantStatRandomize()
        # NOT a reference, but an actual copy. Used to store character stats that are not from items, etc.
        self.baseStats = self.stats.copy()
        # The actual original stats, useful for comparisons, and won't be changed after this.
        self.originalStats = self.stats.copy()
        # Note that this is not a deepcopy.
        self.alive = True
        self.events = None
        self.starterItems = inDict.get('starterItems', [])  # list of strings - we don't process the Items now because Items may not yet be loaded.
        # For efficiency, each contestant stores information about how their
        self.statEventMultipliers = ArenaUtils.DefaultOrderedDict(
            collections.OrderedDict)
        # event probabilities differ from the base. This cannot be fully initialized until the Events are known,
        # and I choose to defer it to its own step in main. statEventMultipliers are calculated off of base stats
        # The rest come from items and perhaps other sources.
        # Note that I _could_ pass in another default dict to give default values,
        self.fullEventMultipliers = ArenaUtils.DefaultOrderedDict(
            collections.OrderedDict)
        # but this isn't actually a good idea (I actually want access attempts to the bottom layer to fail if unavailable). However, every
        # event should have its own dict in here regardless of anything else that is going on, so that's safe.
        self.eventAdditions = ArenaUtils.DefaultOrderedDict(
            collections.OrderedDict)
        # These events cannot happen to this contestant. Default False
        self.eventDisabled = ArenaUtils.DefaultOrderedDict(
            collections.OrderedDict)
    
    def kill(self):
        self.alive = False
        for callback in self.onDeathCallbacks:
            callback(self, self.stateStore[0])
    
    # TODO: HUGE KLUDGE: The easiest way to deploy "escape" right now is just to secretly kill the contestant but not run any of the DeathCallbacks.
    # This may need its own system eventually.
    def escape(self):
        self.alive = False
        
    # Necessary to properly apply special modifiers to combat ability taking items into consideration. Only meant for 1v1 consideration.
    def getCombatAbility(self, otherContestant):
        base_ca = self.stats["combat ability"]
        for item in self.inventory:
            base_ca = item.RealTimeCombatAbilityChange(base_ca, self, otherContestant)
        return base_ca

    def __str__(self):
        return self.name
        
    @property
    def id(self):
        return id(self)

    def contestantStatRandomize(self):
        for statName in self.stats:
            self.stats[statName] = min(max(self.stats[statName] +
                                           random.randint(-1 * self.settings['traitRandomness'], self.settings['traitRandomness']), 0), 10)

    # Fills in missing stats based on a template
    def contestantStatFill(self, statsTemplate):
        # We need a deteriministic order.
        for x in sorted(list(statsTemplate)):
            if x not in self.stats:
                self.baseStats[x] = random.randint(0, 10)
                self.originalStats[x] = self.baseStats[x]
                self.stats[x] = self.baseStats[x]

    @classmethod
    def makeRandomContestant(cls, name, gender, imageFile, statstemplate, settings):
        inDict = collections.OrderedDict()
        inDict['imageFile'] = imageFile
        inDict['stats'] = collections.OrderedDict()
        inDict['gender'] = gender
        for key in statstemplate:
            inDict['stats'][key] = random.randint(0, 10)
        return cls(name, inDict, settings)

    def contestantStatNormalizer(self, target):
        vari = random.uniform(
            1 - self.settings["normalizationRange"], 1 + self.settings["normalizationRange"])
        curSum = sum(self.stats.values())
        modifier = vari * target / curSum
        for i in self.stats:
            self.stats[i] = round(self.stats[i] * modifier)
        # Shuffle overflow stats (>10 or <0) to something else
        for key, value in self.stats.items():
            distribute = 0
            if value < 0:
                distribute = value
                self.stats[key] = 0
            elif value > 10:
                distribute = value - 10
                self.stats[key] = 10
            move = 1 if distribute > 0 else -1
            if move > 0:
                def valid(y): return y < 10
            else:
                def valid(y): return y > 0
            validList = [x for x, y in self.stats.items() if valid(y)]
            for _ in range(abs(distribute)):
                if not len(validList):
                    raise AssertionError(
                        'Stats reached limit in stat normalization!')
                chosen = random.choice(validList)
                self.stats[chosen] += move
                if not valid(self.stats[chosen]):
                    validList.remove(chosen)
        self.baseStats = self.stats.copy()
        self.originalStats = self.stats.copy()

    # Note that each event carries information about which stats affect them
    def InitializeEventModifiers(self, events):
        # This mixing of classes is regrettable but probably necessary
        self.events = events
        for eventName, event in self.events.items():
            # This is kind of a dumb way to do it, but being more general is a pain
            for multiplierType in ['main', 'participant', 'victim']:
                self.eventAdditions[eventName][multiplierType] = 0
                if multiplierType + 'Modifiers' in event.baseProps:
                    self.statEventMultipliers[eventName][multiplierType] = 1
                    for modifier, multiplier in event.baseProps[multiplierType + 'Modifiers'].items():
                        self.statEventMultipliers[eventName][multiplierType] *= (
                            1 + self.settings['statInfluence'])**((self.stats[modifier] - 5) * multiplier)
                    self.fullEventMultipliers[eventName][multiplierType] = self.statEventMultipliers[eventName][multiplierType]

            # NOTE: at the moment, the unique and itemrequired fields can only affect events for which the contestant is the main actor. This may need expansion in the future.
            self.eventDisabled[eventName] = collections.OrderedDict()
            self.eventDisabled[eventName]['main'] = event.baseProps['unique'] or event.baseProps['itemRequired'] or (
                "statusRequired" in event.baseProps and event.baseProps["statusRequired"])
            if event.baseProps['unique']:
                if self.name in event.baseProps['uniqueUsers']:
                    if event.baseProps['itemRequired']:
                        if self.hasThing(event.baseProps['necessaryItem']):
                            self.eventDisabled[eventName]['main'] = False
                    else:
                        self.eventDisabled[eventName]['main'] = False
            elif event.baseProps['itemRequired']:
                if self.hasThing(event.baseProps['necessaryItem']):
                    self.eventDisabled[eventName]['main'] = False
            elif ("statusRequired" in event.baseProps and event.baseProps["statusRequired"]):
                if event.baseProps['necessaryStatus'] in [x.name for x in self.statuses]:
                    self.eventDisabled[eventName]['main'] = False

    # Later on, items will be responsible for manipulating the contestant event modifiers on
    # addition to inventory. This gives an item to perform arbitrary manipulations. For example, this could
    # be done by extending the item class for a particular item and making sure to include the new item class in the list.

    # Note that at the moment a full refresh of the contestant is done each time an item is added or removed. This
    # prevents items from having permanent effects after they are lost (outside of edge cases like directly manipulating
    # self.baseStats, etc. In the future, this could be done by adding a
    # persistent effects field, but this is left out for now. An item.onRemoval(self) is called on removal.

    def hasThing(self, item):
        item_list = [x for x in self.inventory +
                     self.statuses if x.is_same_item(item)]
        return item_list

    # Returns a reference to the instance of the item in the inventory.
    # This effectively spawns new item instances if the return value is not None. If it is undesired that new items be created, it
    # is the responsibility of the caller to ensure the input item and count properly go out of scope/are removed. However, this
    # function assures that it is not being kept alive otherwise.
    # Returns None if item invalid (and nothing was transferred).
    def addItem(self, item, count=1, isNew=True, resetItemAllowed=False, extraArguments=None, target=None):
        if isinstance(item, str):
            item = self.stateStore[0]["items"][item]
        possibleItem = self.hasThing(item)
        if not possibleItem:
            for already_targeted in possibleItem:
                if target == already_targeted.target:
                    return None
                    # TODO: Distinct items might want to impose other rules restructing duplication.
            newItem = ItemInstance.takeOrMakeInstance(item, count=count, target=target, split_stackable=True)
            if not newItem.checkItemValidity(self, isNew, resetItemAllowed):
                return None
            if extraArguments is not None:
                newItem.parseExtraArguments(extraArguments)
            self.inventory.append(newItem)
        elif not item.stackable:
            return None
        else:
            possibleItem[0].count += count
            newItem = possibleItem[0]
        self.refreshEventState()
        return newItem

    # Note that if the caller wants the iteminstance itself, removeAndGet is more appropriate.
    def removeItem(self, item, count=1):
        possibleItem = self.hasThing(item)
        if not possibleItem:
            return False
        if possibleItem[0].count == count:
            self.inventory.remove(possibleItem[0])
            possibleItem[0].onRemoval(self)
        elif possibleItem[0].count < count:
            return False
        else:
            possibleItem[0].count -= count
            if possibleItem[0].count == 0:
                self.inventory.remove(possibleItem[0])
                possibleItem[0].onRemoval(self)
        self.refreshEventState()
        return True

    def removeAndGet(self, item, count=1):
        possibleItem = self.hasThing(item)
        if not possibleItem:
            return None
        if not item.stackable or possibleItem[0].count == count:
            self.inventory.remove(possibleItem[0])
            possibleItem[0].onRemoval(self)
            self.refreshEventState()
            return possibleItem[0]
        if possibleItem[0].count < count:
            return None
        possibleItem[0].count -= count
        self.refreshEventState()
        # We're making a new copy with the right count to pass up.
        return item.copyOrMakeInstance(str(item), count=count)

    def addStatus(self, status, count=1, target=None):
        possibleStatus = self.hasThing(status)
        if isinstance(status, str):
            status = self.stateStore[0]["statuses"][status]
        if not possibleStatus:
            self.statuses.append(StatusInstance.takeOrMakeInstance(status, count=count, target=target))
        elif not status.stackable:
            return False
        else:
            possibleStatus[0].count += count
        self.refreshEventState()
        return True

    def removeStatus(self, status, count=1):
        possibleStatus = self.hasThing(status)
        if not possibleStatus:
            return False
        if possibleStatus[0].count == count:
            self.statuses.remove(possibleStatus[0])
            possibleStatus[0].onRemoval(self)
        elif possibleStatus[0].count < count:
            self.statuses.remove(possibleStatus[0])
            possibleStatus[0].onRemoval(self)
            return False
        else:
            possibleStatus[0].count -= count
        self.refreshEventState()
        return True

    def refreshEventState(self):
        self.stats = self.baseStats.copy()
        self.InitializeEventModifiers(self.events)
        for item in self.inventory + self.statuses:
            item.applyObjectStatChanges(self)
        for item in self.inventory + self.statuses:
            item.onAcquisition(self)

    def permStatChange(self, dictOfChanges):  # NOT to be called by items!
        """dictOfChanges is statName -> change"""
        for statName, change in dictOfChanges.items():
            self.baseStats[statName] += round(change)
        for statName, stat in self.baseStats.items():
            self.baseStats[statName] = max(
                min(self.baseStats[statName], 10), 0)
        self.refreshEventState()
