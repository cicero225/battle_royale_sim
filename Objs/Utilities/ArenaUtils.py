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
    
def weightedDictRandom(inDict, num_sel=1):
    """Given an input dictionary with weights as values, picks num_sel uniformly weighted random selection from the keys"""
    # Selection is without replacement (important for use when picking participants etc.)
    if num_sel > len(inDict):
        raise IndexError
    if not num_sel:
        return ()
    if num_sel == len(inDict):
        return list(inDict.keys())
    keys = []
    allkeys = list(inDict.keys())
    allvalues = list(inDict.values())
    cumsum = [0]
    for weight in allvalues: 
        if weight < 0:
            raise TypeError("Weights of a dictionary for random weight selection cannot be less than 0")
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
    state["callbackStore"]["lastEvent"] = collections.defaultdict(partial(collections.defaultdict, str))

# Logs last event. Must be last callback in overrideContestantEvent. 
def logLastEventByContestant(proceedAsUsual, eventOutputs, thisevent, mainActor, state, participants, victims, sponsorsHere):
    if proceedAsUsual:
        state["callbackStore"]["lastEvent"][state["curPhase"]][mainActor.name] = thisevent.name
    else:
        state["callbackStore"]["lastEvent"][state["curPhase"]][mainActor.name] = "overridden"
    
def killCounterStartup(state):
    state["callbackStore"]["killCounter"] = collections.defaultdict(int)
    
def logKills(proceedAsUsual, eventOutputs, thisevent, mainActor, state, participants, victims, sponsorsHere):
    if not eventOutputs[2] or "murder" not in thisevent.baseProps or not thisevent.baseProps["murder"]:
        return
    if len(eventOutputs)>3:
        killers = eventOutputs[3]
    else:
        killers = [str(x) for x in set([mainActor]+participants+victims) if str(x) not in eventOutputs[2]]
    if not killers:
        return
    for dead in eventOutputs[2]:
        # This dict uses relationship levels to give a weight to how likely it is that someone is the killer
        killDict = {x:1.1**(state["allRelationships"].friendships[str(x)][str(dead)]+2*state["allRelationships"].loveships[str(x)][str(dead)]) for x in killers if str(x)!=str(dead)}
        trueKiller = weightedDictRandom(killDict)[0]
        state["callbackStore"]["killCounter"][str(trueKiller)] += 1
        # This is treated as if someone had done the worst possible thing to the dead person
        state["allRelationships"].IncreaseFriendLevel(state["contestants"][str(dead)], state["contestants"][str(trueKiller)], -10)
        state["allRelationships"].IncreaseLoveLevel(state["contestants"][str(dead)], state["contestants"][str(trueKiller)], -10)
        
def killWrite(state):
    #TODO: look up how html tables work when you have internet... And make this include everyone (not just successful killers)
    killWriter = HTMLWriter()
    killWriter.addTitle("Day "+str(state["turnNumber"][0])+" Kills")
    for contestant, kills in state["callbackStore"]["killCounter"].items():
        desc = 'Kills: ' + str(kills)
        descContestant = state["contestants"][contestant]
        if not descContestant.alive:
            desc += ' - DEAD'
        killWriter.addEvent(desc, [descContestant])
    killWriter.finalWrite(os.path.join("Assets",str(state["turnNumber"][0])+" Kills.html"))
    return False
    
def endHypothermiaIfDayHasPassed(state):
    for contestant in state["contestants"].values():
        if contestant.hypothermic and contestant.hypothermic<=state["turnNumber"][0]-1:
            contestant.SetUnhypothermic()
    
# Rig it so the same event never happens twice to the same person in the same phase(makes game feel better)
def eventMayNotRepeat(actor, origProb, event, state): 
    if state["callbackStore"]["lastEvent"][state["curPhase"]][actor.name] == event.name: 
        return 0, False
    return origProb, True
  
# Ends the game if only one contestant left  
def onlyOneLeft(liveContestants, _):
    if len(liveContestants) == 1:
        return True
    return False