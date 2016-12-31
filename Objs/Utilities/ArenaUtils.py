"""Utility functions for battle royale sim"""
from __future__ import division 

import json
import random
import bisect
import collections
    
def weightedDictRandom(inDict, num_sel=1):
    """Given an input dictionary with weights as values, picks num_sel uniformly weighted random selection from the keys"""
    # Selection is without replacement (important for use when picking participants etc.)
    if num_sel > len(inDict):
        raise IndexError
    if not num_sel:
        return ()
    if num_sel == len(inDict):
        return inDict.keys() if num_sel > 1 else list(inDict.keys())[0]
    keys = []
    allkeys = list(inDict.keys())
    allvalues = list(inDict.values())
    cumsum = [0]
    for weight in allvalues: 
        cumsum.append(cumsum[-1]+weight)
    for dummy in range(num_sel):
        thisrand = random.uniform(1e-100,cumsum[-1]-1e-100) #The 1e-100 is important for numerical reasons
        selected = bisect.bisect_left(cumsum,thisrand)-1
        keys.append(allkeys.pop(selected))
        if dummy != num_sel-1:
            remWeight = allvalues.pop(selected)
            for x in range(selected+1,len(cumsum)):
                cumsum[x] -= remWeight
            cumsum.pop(selected+1)
    return keys

def LoadJSONIntoDictOfObjects(path, settings, objectType):
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
    try:
        with open(path) as file:
            fromFile = json.load(file)
    except TypeError:
        fromFile = json.load(path)

    objectDict = {}
    for name in fromFile:
        objectDict[name] = objectType(name, fromFile[name], settings) # Constructor should \
                                                                  # take in dict and settings (also a dict)
    return objectDict

# Callbacks for specific arena features

def logLastEventStartup(state):
    state["callbackStore"]["lastEvent"] = collections.defaultdict(str)

# Logs last event. Must be last callback in overrideContestantEvent. 
def logLastEventByContestant(contestantKey, eventName, state, proceedAsUsual):
    if proceedAsUsual:
        state["callbackStore"]["lastEvent"][contestantKey] = eventName
    else:
        state["callbackStore"]["lastEvent"][contestantKey] = "overridden"
    return proceedAsUsual

# Rig it so the same event never happens twice to the same person (makes game feel better)
def eventMayNotRepeat(actor, origProb , event, state): 
    if state["callbackStore"]["lastEvent"][actor.name] == event.name: 
        return 0, False
    return origProb, True
  
# Ends the game if only one contestant left  
def onlyOneLeft(liveContestants, _):
    if len(liveContestants) == 1:
        return True
    return False