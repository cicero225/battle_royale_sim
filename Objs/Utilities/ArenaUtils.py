"""Utility functions for battle royale sim"""
from __future__ import division
from Objs.Display.HTMLWriter import HTMLWriter
from functools import partial

import json
import os
import random
import bisect
import collections
import html
import copy
import math
from weakref import proxy

# Needed a merged default/OrderedDict for some applications

class DefaultOrderedDict(collections.OrderedDict):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
                not callable(default_factory)):
            raise TypeError('first argument must be callable')
        collections.OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return collections.OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(list(self.items()), memo))

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                               collections.OrderedDict.__repr__(self))

# Modified from https://github.com/ActiveState/code/blob/3b27230f418b714bc9a0f897cb8ea189c3515e99/recipes/Python/576696_OrderedSet_with_Weakrefs/recipe-576696.py
class Link(object):
    __slots__ = 'prev', 'next', 'key', '__weakref__'

class OrderedSet(collections.MutableSet):
    'Set the remembers the order elements were added'
    # Big-O running times for all methods are the same as for regular sets.
    # The internal self.__map dictionary maps keys to links in a doubly linked list.
    # The circular doubly linked list starts and ends with a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # The prev/next links are weakref proxies (to prevent circular references).
    # Individual links are kept alive by the hard reference in self.__map.
    # Those hard references disappear when a key is deleted from an OrderedSet.

    def __init__(self, iterable=None):
        self.__root = root = Link()         # sentinel node for doubly linked list
        root.prev = root.next = root
        self.__map = {}                     # key --> link
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.__map)

    def __contains__(self, key):
        return key in self.__map

    def add(self, key):
        # Store new key in a new link at the end of the linked list
        if key not in self.__map:
            self.__map[key] = link = Link()            
            root = self.__root
            last = root.prev
            link.prev, link.next, link.key = last, root, key
            last.next = root.prev = proxy(link)

    def discard(self, key):
        # Remove an existing item using self.__map to find the link which is
        # then removed by updating the links in the predecessor and successors.        
        if key in self.__map:        
            link = self.__map.pop(key)
            link.prev.next = link.next
            link.next.prev = link.prev
            
    def update(self, iterable):
        for key in iterable:
            self.add(key)

    def __iter__(self):
        # Traverse the linked list in order.
        root = self.__root
        curr = root.next
        while curr is not root:
            yield curr.key
            curr = curr.next

    def __reversed__(self):
        # Traverse the linked list in reverse order.
        root = self.__root
        curr = root.prev
        while curr is not root:
            yield curr.key
            curr = curr.prev

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = next(reversed(self)) if last else next(iter(self))
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return not self.isdisjoint(other)

# scipy inverse error function

def polevl(x, coefs, N):
    ans = 0
    power = len(coefs) - 1
    for coef in coefs:
        ans += coef * x**power
        power -= 1
    return ans


def p1evl(x, coefs, N):
    return polevl(x, [1] + coefs, N)


def inv_erf(z):
    if z < -1 or z > 1:
        raise ValueError("`z` must be between -1 and 1 inclusive")
    if z == 0:
        return 0
    if z == 1:
        return math.inf
    if z == -1:
        return -math.inf
    # From scipy special/cephes/ndrti.c

    def ndtri(y):
        # approximation for 0 <= abs(z - 0.5) <= 3/8
        P0 = [
            -5.99633501014107895267E1,
            9.80010754185999661536E1,
            -5.66762857469070293439E1,
            1.39312609387279679503E1,
            -1.23916583867381258016E0,
        ]
        Q0 = [
            1.95448858338141759834E0,
            4.67627912898881538453E0,
            8.63602421390890590575E1,
            -2.25462687854119370527E2,
            2.00260212380060660359E2,
            -8.20372256168333339912E1,
            1.59056225126211695515E1,
            -1.18331621121330003142E0,
        ]
        # Approximation for interval z = sqrt(-2 log y ) between 2 and 8
        # i.e., y between exp(-2) = .135 and exp(-32) = 1.27e-14.
        P1 = [
            4.05544892305962419923E0,
            3.15251094599893866154E1,
            5.71628192246421288162E1,
            4.40805073893200834700E1,
            1.46849561928858024014E1,
            2.18663306850790267539E0,
            -1.40256079171354495875E-1,
            -3.50424626827848203418E-2,
            -8.57456785154685413611E-4,
        ]
        Q1 = [
            1.57799883256466749731E1,
            4.53907635128879210584E1,
            4.13172038254672030440E1,
            1.50425385692907503408E1,
            2.50464946208309415979E0,
            -1.42182922854787788574E-1,
            -3.80806407691578277194E-2,
            -9.33259480895457427372E-4,
        ]
        # Approximation for interval z = sqrt(-2 log y ) between 8 and 64
        # i.e., y between exp(-32) = 1.27e-14 and exp(-2048) = 3.67e-890.
        P2 = [
            3.23774891776946035970E0,
            6.91522889068984211695E0,
            3.93881025292474443415E0,
            1.33303460815807542389E0,
            2.01485389549179081538E-1,
            1.23716634817820021358E-2,
            3.01581553508235416007E-4,
            2.65806974686737550832E-6,
            6.23974539184983293730E-9,
        ]
        Q2 = [
            6.02427039364742014255E0,
            3.67983563856160859403E0,
            1.37702099489081330271E0,
            2.16236993594496635890E-1,
            1.34204006088543189037E-2,
            3.28014464682127739104E-4,
            2.89247864745380683936E-6,
            6.79019408009981274425E-9,
        ]
        s2pi = 2.50662827463100050242
        code = 1
        if y > (1.0 - 0.13533528323661269189):      # 0.135... = exp(-2)
            y = 1.0 - y
            code = 0
        if y > 0.13533528323661269189:
            y = y - 0.5
            y2 = y * y
            x = y + y * (y2 * polevl(y2, P0, 4) / p1evl(y2, Q0, 8))
            x = x * s2pi
            return x
        x = math.sqrt(-2.0 * math.log(y))
        x0 = x - math.log(x) / x
        z = 1.0 / x
        if x < 8.0:                 # y > exp(-32) = 1.2664165549e-14
            x1 = z * polevl(z, P1, 8) / p1evl(z, Q1, 8)
        else:
            x1 = z * polevl(z, P2, 8) / p1evl(z, Q2, 8)
        x = x0 - x1
        if code != 0:
            x = -x
        return x
    result = ndtri((z + 1) / 2.0) / math.sqrt(2)
    return result


def weightedDictRandom(inDict, num_sel=1):
    """Given an input dictionary with weights as values, picks num_sel uniformly weighted random selection from the keys"""
    # Selection is without replacement (important for use when picking participants etc.)
    if not inDict:
        return ()
    if num_sel > len(inDict):
        raise IndexError
    if not num_sel:
        return ()
    if num_sel == len(inDict):
        return list(inDict.keys())
    keys = []
    allkeys = list(inDict.keys())
    # Minimize floating point precision problems by scaling the lower probabilities if necessary.
    max_value = max(inDict.values())
    allvalues = []
    for x in inDict.values():
        allvalues.append(x if x > max_value*1e-15 else max_value*1e-15)
    cumsum = [0]
    for weight in allvalues:
        if weight < 0:
            raise TypeError(
                "Weights of a dictionary for random weight selection cannot be less than 0")
        cumsum.append(cumsum[-1] + weight)
    for dummy in range(num_sel):
        # The 1e-100 is important for numerical reasons
        thisrand = random.uniform(cumsum[1]*1e-100, cumsum[-1]*(1 - 1e-100))
        selected = bisect.bisect_left(cumsum, thisrand) - 1
        keys.append(allkeys.pop(selected))
        if dummy != num_sel - 1:
            remWeight = allvalues.pop(selected)
            for x in range(selected + 1, len(cumsum)):
                cumsum[x] -= remWeight
            cumsum.pop(selected + 1)
    return keys

# converts a regular dict into a sorted, ordered dict for better determinism.


def DictToOrderedDict(d):
    objectDict = collections.OrderedDict()
    try:
        orderedNames = sorted(d.keys())
    except TypeError:
        orderedNames = sorted(d.keys(), key=lambda x: str(x))
    for name in orderedNames:
        objectDict[name] = d[name]
    return objectDict

# By default, json load returns arbitrary dict and list orders, which is bad for determinsm. Use this instead.


def JSONOrderedLoad(path):
    try:
        with open(path) as file:
            fromFile = json.load(file)
    except TypeError:
        fromFile = json.load(path)

    def SortListOrDict(thing):
        if type(thing) == dict:
            thing = DictToOrderedDict(thing)
            for sub, value in thing.items():
                if (type(value) == list) or (type(value) == dict):
                    thing[sub] = SortListOrDict(value)
        else:
            thing = sorted(thing)
            for i, value in enumerate(thing):
                if (type(value) == list) or (type(value) == dict):
                    thing[i] = SortListOrDict(value)
        return thing
    return SortListOrDict(fromFile)


def LoadJSONIntoDictOfObjects(path, settings, objectType):
    # TODO: this does not properly order subdicts from the .json loaded dict that are more than one deep.
    """
    # Args: path is the path or file handle to the json
    #       settings is the settings dict, itself loaded from JSON (but not by this)
    #       objectType is the class of the object (can be passed in Python)
    #
    # Returns: dict with keys corresponding to object names and values corresponding to the objects formed. This is effectively
    # a table of these objects. (A table of contestants, sponsors, etc.)
    #
    # Notes: Path is typically something like os.path.join('Contestants', 'Constestant.json') but let's not assume that.
    #
    """
    fromFile = JSONOrderedLoad(path)

    objectDict = collections.OrderedDict()
    for name in fromFile:
        # Constructor should take in dict and settings (also a dict)
        objectDict[name] = objectType(name, fromFile[name], settings)

    return objectDict

# Callbacks for specific arena features


def loggingStartup(state):
    state["callbackStore"]["eventLog"] = DefaultOrderedDict(partial(
        DefaultOrderedDict, partial(DefaultOrderedDict, str)))  # Crazy nesting...
    state["callbackStore"]["killCounter"] = DefaultOrderedDict(list)
    state["callbackStore"]["contestantLog"] = DefaultOrderedDict(dict)

# Logs last event. Must be last callback in overrideContestantEvent.


def logEventsByContestant(proceedAsUsual, eventOutputs, thisevent, mainActor, state, participants, victims, sponsorsHere):
    if proceedAsUsual:
        state["callbackStore"]["eventLog"][state["turnNumber"][0]
                                           ][state["curPhase"]][mainActor.name] = thisevent.name
    else:
        state["callbackStore"]["eventLog"][state["turnNumber"][0]
                                           ][state["curPhase"]][mainActor.name] = "overridden"


def logKills(proceedAsUsual, eventOutputs, thisevent, mainActor, state, participants, victims, sponsorsHere):
    if not eventOutputs[2] or (len(eventOutputs) <= 3 and ("murder" not in thisevent.baseProps or not thisevent.baseProps["murder"])):
        return
    if (len(eventOutputs) > 3 and isinstance(eventOutputs[3], dict)):
        killers = []
        trueKillDict = eventOutputs[3]
    else:
        killers = sorted([str(x)
                          for x in set([mainActor] + participants + victims)])
        trueKillDict = collections.OrderedDict()
    if not (killers or trueKillDict):
        return
    trueKillCounterDict = collections.OrderedDict()
    for dead in eventOutputs[2]:
        if killers:
            # This dict uses relationship levels to give a weight to how likely it is that someone is the killer
            killDict = DictToOrderedDict({x: 1.1**(state["allRelationships"].friendships[str(x)][str(
                dead)] + 2 * state["allRelationships"].loveships[str(x)][str(dead)]) for x in killers if str(x) != str(dead)})
            # This can happen if the only potential killer is also someone who died in the event.
            if not killDict:
                continue
            trueKiller = weightedDictRandom(killDict)[0]
            trueKillDict[str(dead)] = str(trueKiller)
        else:
            trueKiller = trueKillDict[str(dead)]
        if str(trueKiller) not in trueKillCounterDict:
            trueKillCounterDict[str(
                trueKiller)] = len(state["callbackStore"]["killCounter"][str(trueKiller)])
        state["callbackStore"]["killCounter"][str(trueKiller)].append(dead)
        state["callbackStore"]["KillThisTurnFlag"][str(trueKiller)] = True
        # if str(trueKiller) != str(mainActor):
        # This is treated as if someone had done the worst possible thing to the dead person. There is also a stability impact.
        # We have to check for suicide, which is barely possible (e.g. by a trap)
        if str(trueKiller) != str(dead):
            state["allRelationships"].IncreaseFriendLevel(
                state["contestants"][str(dead)], state["contestants"][str(trueKiller)], -10)
            state["allRelationships"].IncreaseLoveLevel(
                state["contestants"][str(dead)], state["contestants"][str(trueKiller)], -10)
            state["allRelationships"].KillImpact(dead)

    # Modify description to reflect kills
    killString = " [Kills: "
    killList = []
    for key, value in trueKillDict.items():
        trueKillCounterDict[value] += 1
        killList.append(
            value + " (" + str(trueKillCounterDict[value]) + ")" + " kills " + key)
    killString += ", ".join(killList) + "]"
    eventOutputs[0] += killString


def logContestants(liveContestants, baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, baseEventSponsorWeights, turnNumber, state):
    state["callbackStore"]["contestantLog"][turnNumber[0]] = liveContestants


def resetKillFlag(liveContestants, baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, baseEventSponsorWeights, turnNumber, state):
    state["callbackStore"]["KillThisTurnFlag"] = DefaultOrderedDict(dict)


def killWrite(state):
    from Objs.Events.Event import Event
    killWriter = HTMLWriter(state["statuses"])
    killWriter.addTitle("Day " + str(state["turnNumber"][0]) + " Kills")
    for contestant, kills in state["callbackStore"]["killCounter"].items():
        desc = str(contestant) + '<br/>Kills: ' + str(len(kills)) + '<br/>' + Event.englishList(kills, False)
        descContestant = state["contestants"][contestant]
        if not descContestant.alive:
            desc = '(DEAD) ' + desc
        killWriter.addEvent(desc, [descContestant])
    killWriter.finalWrite(os.path.join("Assets", str(
        state["turnNumber"][0]) + " Kills.html"), state)
    return False

def sponsorTraitWrite(state):
    sponsorWriter = HTMLWriter(state["statuses"])
    sponsorWriter.addTitle("Sponsor Traits")
    for sponsor in state["sponsors"].values():
        sponsorWriter.addEvent("Primary Trait: " + sponsor.primary_trait +
                               "<br> Secondary Trait: " + sponsor.secondary_trait, [sponsor])
    sponsorWriter.finalWrite(os.path.join(
        "Assets", "Sponsor Traits.html"), state)

def initializeRomances(state):
    relationships = state["allRelationships"]
    # Deliberate copy
    new_list = list(state["contestants"].values())
    random.shuffle(new_list)  # Otherwise, candidates earlier in the alphabet by file name will get inapparopriate bias towards romances.
    for contestant in new_list:
        if not contestant.hasThing("Love"):
            relationships.SetNewRomance(contestant, initial=True)

# Adds a Shipping Update immediately after a relevant event.
def relationshipUpdate(thisWriter, eventOutputs, thisEvent, state):
    new_loves, lost_loves, new_hates, lost_hates = state["allRelationships"].reportChanges(
    )
    contestants = state["contestants"]
    heart = state["statuses"]["Love"]
    arrow = state["statuses"]["RightArrow"]
    heartbroken = state["statuses"]["LoveBroken"]

    # TODO(This code needs considerable simplification)
    for contestant_tuple, _ in new_loves.items():
        lover1 = contestants[contestant_tuple[0]]
        lover2 = contestants[contestant_tuple[1]]
        # We only check for new romances or crushes if a contestant does not already have one.
        if lover1.hasThing("Love") or lover2.hasThing("Love"):
            continue
        if (contestant_tuple[1], contestant_tuple[0]) not in lost_loves:
            lover1.removeStatus("LoveBroken")
            lover2.removeStatus("LoveBroken")
            lover1.addStatus("Love", target=lover2)
            lover2.addStatus("Love", target=lover1)
            thisWriter.addEvent(contestant_tuple[0] + " and " + contestant_tuple[1] + " are now in a romance.", [
                                lover1, heart, lover2])
            continue
        thisWriter.addEvent(contestant_tuple[0] + " now has a crush on " + contestant_tuple[1], [
                            lover1, heart, arrow, lover2])
    
    skiptuples = set()
    for contestant_tuple, old_backwards_exists in lost_loves.items():
        if contestant_tuple in skiptuples:
            continue
        lover1 = contestants[contestant_tuple[0]]
        lover2 = contestants[contestant_tuple[1]]
        reverse_tuple = (contestant_tuple[1], contestant_tuple[0])
        potential_love = lover1.hasThing("Love")
        if potential_love:
            potential_love = potential_love[0]
        if old_backwards_exists and not potential_love:
            thisWriter.addEvent(contestant_tuple[0] + " no longer has a crush on " + contestant_tuple[1], [
                                lover1, heartbroken, arrow, lover2])
        elif not old_backwards_exists and potential_love and potential_love.target == contestant_tuple[1]:
            thisWriter.addEvent(contestant_tuple[0] + " and " + contestant_tuple[1] + " are no longer in a romance.", [
                                lover1, heartbroken, lover2])
            skiptuples.add(reverse_tuple)
            new_lover = state["allRelationships"].SetNewRomance(contestant_tuple[0])
            if new_lover:
                thisWriter.addEvent(contestant_tuple[0] + " is now in a romance with " + str(new_lover), [lover1, heart, new_lover])
            new_lover = state["allRelationships"].SetNewRomance(contestant_tuple[1])
            if new_lover:
                thisWriter.addEvent(contestant_tuple[1] + " is now in a romance with " + str(new_lover), [lover2, heart, new_lover])
            continue

    swords = state["statuses"]["Swords"]
    swordsbroken = state["statuses"]["SwordsBroken"]
    skiptuples = set()
    for contestant_tuple, old_backwards_exists in new_hates.items():
        if contestant_tuple in skiptuples:
            continue
        reverse_tuple = (contestant_tuple[1], contestant_tuple[0])
        if old_backwards_exists:
            if reverse_tuple not in lost_hates:
                thisWriter.addEvent(contestant_tuple[0] + " and " + contestant_tuple[1] + " are now dire enemies.", [
                                    contestants[contestant_tuple[0]], swords, contestants[contestant_tuple[1]]])
                continue
            thisWriter.addEvent(contestant_tuple[0] + " now hates " + contestant_tuple[1], [
                                contestants[contestant_tuple[0]], swords, arrow, contestants[contestant_tuple[1]]])
        else:
            if reverse_tuple in new_hates:
                thisWriter.addEvent(contestant_tuple[0] + " and " + contestant_tuple[1] + " are now dire enemies.", [
                                    contestants[contestant_tuple[0]], swords, contestants[contestant_tuple[1]]])
                skiptuples.add(reverse_tuple)
                continue
            thisWriter.addEvent(contestant_tuple[0] + " now hates " + contestant_tuple[1], [
                                contestants[contestant_tuple[0]], swords, arrow, contestants[contestant_tuple[1]]])
    skiptuples = set()
    for contestant_tuple, old_backwards_exists in lost_hates.items():
        if contestant_tuple in skiptuples:
            continue
        reverse_tuple = (contestant_tuple[1], contestant_tuple[0])
        if old_backwards_exists:
            thisWriter.addEvent(contestant_tuple[0] + " no longer hates " + contestant_tuple[1], [
                                contestants[contestant_tuple[0]], swordsbroken, arrow, contestants[contestant_tuple[1]]])
        else:
            if reverse_tuple in lost_hates:
                thisWriter.addEvent(contestant_tuple[0] + " and " + contestant_tuple[1] + " are no longer dire enemies.", [
                                    contestants[contestant_tuple[0]], swordsbroken, contestants[contestant_tuple[1]]])
                skiptuples.add(reverse_tuple)
                continue
            thisWriter.addEvent(contestant_tuple[0] + " no longer hates " + contestant_tuple[1], [
                                contestants[contestant_tuple[0]], swordsbroken, arrow, contestants[contestant_tuple[1]]])

def ContestantStatWrite(state):
    from Objs.Events.Event import Event

    statWriter = HTMLWriter(state["statuses"])
    statWriter.addTitle("Contestant Summary")
    for contestant in state["contestants"].values():
        if not contestant.alive:
            continue
        # Construct stats and items line
        eventLine = str(contestant) + "<br/>" + \
            Event.englishList(contestant.inventory + contestant.statuses)
        for statname, curstat in contestant.stats.items():
            origstat = contestant.originalStats[statname]
            eventLine += "<br/>" + statname + ": " + str(origstat)
            diff = curstat - origstat
            if diff > 0:
                eventLine += " " + HTMLWriter.wrap("+" + str(diff), "positive")
            elif diff < 0:
                eventLine += " " + HTMLWriter.wrap("-" + str(-diff), "negative")
        statWriter.addEvent(eventLine, [contestant])
    statWriter.finalWrite(os.path.join("Assets", str(
        state["turnNumber"][0]) + " Stats.html"), state)

def starterItemAllocation(state):
    if state["settings"]["presetStarterItems"]:
        for contestant in state["contestants"].values():
            for newItemName in contestant.starterItems:
                contestant.addItem(newItemName, isNew=True, resetItemAllowed=True)
    if state["settings"]["randomStarterItems"] > 0:
        allItemStrings = set(str(x) for x in state["items"].values())
        for contestant in state["contestants"].values():
            options = sorted(allItemStrings - set(str(x) for x in contestant.inventory if not x.stackable), key=lambda x: str(x))
            for _ in range(max(state["settings"]["randomStarterItems"] - len(contestant.inventory), 0)):
                if not options:
                    continue
                choice = random.choice(options)
                itemInstance = contestant.addItem(choice, isNew=True, resetItemAllowed=True)
                if not itemInstance.stackable:
                    options.remove(choice)
        
# Rig it so the same event never happens twice to the same person in consecutive turns (makes game feel better)

def eventMayNotRepeat(actor, origProb, event, state):
    # This process doesn't work at all for phases with only one event, so exclude those too
    if (state["curPhase"] not in state["phases"]["deduplicate"]) or (sum(1 for x in state['events'].values() if "phase" not in x.baseProps or state["curPhase"] in x.baseProps["phase"]) == 1):
        return origProb, True
    # Since defaultdict, this would work fine even without this check, but this makes it more explicit (and is more robust to future changes)
    if state["turnNumber"][0] > 1:
        for x in state["callbackStore"]["eventLog"][state["turnNumber"][0] - 1].values():
            if x[actor.name] == event.name:
                return 0, False
    return origProb, True

# Ends the game if only one contestant left

def onlyOneLeft(liveContestants, _):
    if len(liveContestants) == 1:
        return True
    return False

    
 # Debug methods, stored for convenience
def giveEveryoneItem(item, state):
    for contestant in state["contestants"].values():
        contestant.addItem(item, isNew=True, resetItemAllowed=True)
        
        
# Legacy, should be removed eventually

def relationshipWrite(state):
    relationships = state["allRelationships"]
    firstTurn = ("relationshipLastTurn" not in state["callbackStore"])
    if not firstTurn:
        oldRelationshipsFriendships = state["callbackStore"]["relationshipLastTurn"]["friendships"]
        oldRelationshipsLoveships = state["callbackStore"]["relationshipLastTurn"]["loveships"]
    state["callbackStore"]["relationshipLastTurn"] = collections.OrderedDict()
    state["callbackStore"]["relationshipLastTurn"]["friendships"] = copy.deepcopy(
        relationships.friendships)
    state["callbackStore"]["relationshipLastTurn"]["loveships"] = copy.deepcopy(
        relationships.loveships)

    friendWriter = HTMLWriter(state["statuses"])
    friendWriter.addTitle(
        "Day " + str(state["turnNumber"][0]) + " Friendships")
    loveWriter = HTMLWriter(state["statuses"])
    loveWriter.addTitle("Day " + str(state["turnNumber"][0]) + " Romances")
    # A hack to get around importing Events
    anyEvent = next(iter(state["events"].values()))
    for person in list(state["contestants"].values()) + list(state["sponsors"].values()):
        if not person.alive:
            continue
        friendLine = str(person)
        friendList = []
        lostFriendList = []
        enemyList = []
        lostEnemyList = []
        liveFriends = {x: y for x, y in relationships.friendships[str(person)].items(
        ) if x in state["contestants"] and state["contestants"][x].alive}
        liveFriends.update({x: y for x, y in relationships.friendships[str(
            person)].items() if x in state["sponsors"]})
        sortFriends = collections.OrderedDict()
        for x in sorted(liveFriends, key=liveFriends.get, reverse=True):
            sortFriends[x] = liveFriends[x]
        for key, value in sortFriends.items():
            if value >= 4:
                writeString = key
                if not firstTurn:
                    if oldRelationshipsFriendships[str(person)][key] < 4:
                        writeString += ' (New!) '
                if relationships.friendships[key][str(person)] >= 4:
                    friendList.append(writeString)
                else:
                    friendList.append(writeString + ' (Not Mutual)')
            else:
                if not firstTurn:
                    if oldRelationshipsFriendships[str(person)][key] >= 4:
                        tempString = key
                        if oldRelationshipsFriendships[str(person)][key] < 4:
                            tempString += ' (Not Mutual)'
                        lostFriendList.append(tempString)
            if value <= -4:
                writeString = key
                if not firstTurn:
                    if oldRelationshipsFriendships[str(person)][key] > -4:
                        writeString += ' (New!) '
                if relationships.friendships[key][str(person)] <= -4:
                    enemyList.append(writeString)
                else:
                    enemyList.append(writeString + ' (Not Mutual)')
            else:
                if not firstTurn:
                    if oldRelationshipsFriendships[str(person)][key] <= -4:
                        tempString = key
                        if oldRelationshipsFriendships[key][str(person)] > -4:
                            tempString += ' (Not Mutual)'
                        lostEnemyList.append(tempString)
        if friendList:
            friendLine += "<br> Friend: "
            friendLine += anyEvent.englishList(friendList, False)
        if lostFriendList:
            friendLine += "<br> No Longer Friends: "
            friendLine += anyEvent.englishList(lostFriendList, False)
        if enemyList:
            friendLine += "<br> Enemies: "
            friendLine += anyEvent.englishList(enemyList, False)
        if lostEnemyList:
            friendLine += "<br> No Longer Enemies: "
            friendLine += anyEvent.englishList(lostEnemyList, False)
        if friendList or lostFriendList:
            friendWriter.addEvent(friendLine, [person])

        loveLine = str(person)
        loveList = []
        lostLoveList = []
        loveEnemyList = []
        lostLoveEnemyList = []
        liveLoves = {x: y for x, y in relationships.loveships[str(person)].items(
        ) if x in state["contestants"] and state["contestants"][x].alive}
        liveLoves.update({x: y for x, y in relationships.loveships[str(
            person)].items() if x in state["sponsors"]})
        sortLoves = collections.OrderedDict()
        for x in sorted(liveLoves, key=liveLoves.get, reverse=True):
            sortLoves[x] = liveLoves[x]
        for key, value in sortLoves.items():
            if value >= 4:
                writeString = key
                if not firstTurn:
                    if oldRelationshipsLoveships[str(person)][key] < 4:
                        writeString += ' (New!) '
                if relationships.loveships[key][str(person)] >= 4:
                    loveList.append(writeString)
                else:
                    loveList.append(writeString + ' (Not Mutual)')
            else:
                if not firstTurn:
                    if oldRelationshipsLoveships[str(person)][key] >= 4:
                        tempString = key
                        if oldRelationshipsLoveships[key][str(person)] < 4:
                            tempString += ' (Not Mutual)'
                        lostLoveList.append(tempString)
            if value <= -4:
                writeString = key
                if not firstTurn:
                    if oldRelationshipsLoveships[str(person)][key] > -4:
                        writeString += ' (New!) '
                if relationships.loveships[key][str(person)] <= -4:
                    loveEnemyList.append(writeString)
                else:
                    loveEnemyList.append(writeString + ' (Not Mutual)')
            else:
                if not firstTurn:
                    if oldRelationshipsLoveships[str(person)][key] <= -4:
                        tempString = key
                        if oldRelationshipsLoveships[key][str(person)] > -4:
                            tempString += ' (Not Mutual)'
                        lostLoveEnemyList.append(key)
        if loveList:
            loveLine += "<br> Romances: "
            loveLine += anyEvent.englishList(loveList, False)
        if lostLoveList:
            loveLine += "<br> No Longer Lovers: "
            loveLine += anyEvent.englishList(lostLoveList, False)
        if loveEnemyList:
            loveLine += "<br> Romantic Enemies: "
            loveLine += anyEvent.englishList(loveEnemyList, False)
        if lostLoveEnemyList:
            loveLine += "<br> No Longer Romantic Enemies: "
            loveLine += anyEvent.englishList(lostLoveEnemyList, False)

        if loveList or lostLoveList:
            loveWriter.addEvent(loveLine, [person])

    friendWriter.finalWrite(os.path.join("Assets", str(
        state["turnNumber"][0]) + " Friendships.html"), state)
    loveWriter.finalWrite(os.path.join("Assets", str(
        state["turnNumber"][0]) + " Romances.html"), state)
        
def injuryAndStatusWrite(state):
    # aren't circular import dependencies fun...
    from Objs.Events.Event import Event

    def writeObjectInventory(filename, inventory_attr_name):
        Writer = HTMLWriter(state["statuses"])
        Writer.addTitle(
            "Day " + str(state["turnNumber"][0]) + " " + filename + " Accumulated")
        for contestant in state["contestants"].values():
            if not contestant.alive or not getattr(contestant, inventory_attr_name):
                continue
            eventLine = str(contestant) + ": " + \
                Event.englishList(getattr(contestant, inventory_attr_name))
            Writer.addEvent(eventLine, [contestant] +
                            getattr(contestant, inventory_attr_name))
        Writer.finalWrite(os.path.join("Assets", str(
            state["turnNumber"][0]) + " " + filename + ".html"), state)
    writeObjectInventory("Items", "inventory")
    writeObjectInventory("Statuses", "statuses")