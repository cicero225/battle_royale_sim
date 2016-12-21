"""Utility functions for battle royale sim"""
from __future__ import division 

import json
import random
import bisect
    
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
    return (keys if num_sel > 1 else keys[0])

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

    
# May eventually factor relationship stuff into own object, but for now this is fine
def relationsMainWeightCallback(friendships, loveships, settings, actor, baseEventActorWeight, event):
    if event.baseProps["mainFriendEffect"]:
        negOrPos = 1 if event.baseProps["mainNeededFriendLevel"]["relation"] else -1
        for friendLevel in friendships[actor.name].values():
            if negOrPos*friendLevel >= event.baseProps["mainNeededFriendLevel"]["value"]:
                baseEventActorWeight *= (1+settings["relationInfluence"])**event.baseProps["mainFriendEffect"]
                break
    if event.baseProps["mainLoveEffect"]:
        negOrPos = 1 if event.baseProps["mainNeededLoveLevel"]["relation"] else -1
        for loveLevel in loveships[actor.name].values():
            if negOrPos*loveLevel >= event.baseProps["mainNeededLoveLevel"]["value"]:
                baseEventActorWeight *= (1+settings["relationInfluence"])**event.baseProps["mainLoveEffect"]
                break
    return (baseEventActorWeight, True)

    
def relationsParticipantWeightCallback(friendships, loveships, settings, actor, participant, baseEventParticipantWeight, event):
    if "friendRequired" in event.baseProps and event.baseProps["friendRequired"]:
        negOrPos = 1 if event.baseProps["neededFriendLevel"]["relation"] else -1
        if negOrPos*friendships[actor.name][participant.name]<negOrPos*event.baseProps["neededFriendLevel"]["value"]:
            return (0, False)
        if "mutual" in event.baseProps and event.baseProps["mutual"]:
            if negOrPos*friendships[participant.name][actor.name]<negOrPos*event.baseProps["neededFriendLevel"]["value"]:
                return (0, False)
    if "loveRequired" in event.baseProps and event.baseProps["loveRequired"]:
        negOrPos = 1 if event.baseProps["neededLoveLevel"]["relation"] else -1
        if negOrPos*loveships[actor.name][participant.name]<negOrPos*event.baseProps["NeededLoveLevel"]["value"]:
            return (0, False)
        if "mutual" in event.baseProps and event.baseProps["mutual"]:
            if negOrPos*loveships[participant.name][actor.name]<negOrPos*event.baseProps["neededLoveLevel"]["value"]:
                return (0, False)
    friendlevel = friendships[actor.name][participant.name]
    lovelevel = loveships[actor.name][participant.name]
    if "mutual" in event.baseProps and event.baseProps["mutual"]:
        friendlevel = (friendlevel+friendships[participant.name][actor.name])/2
        lovelevel = (lovelevel+loveships[participant.name][actor.name])/2
    return(baseEventParticipantWeight*
          (1+settings["relationInfluence"])**(friendlevel*event.baseProps["friendEffect"])*
          (1+settings["relationInfluence"])**(lovelevel*event.baseProps["loveEffect"]),
          True)
 
 
def relationsVictimWeightCallback(friendships, loveships, settings, actor, victim, baseEventVictimWeight, event):
    if "friendRequiredVictim" in event.baseProps and event.baseProps["friendRequiredVictim"]: 
        negOrPos = 1 if event.baseProps["neededFriendLevelVictim"]["relation"] else -1
        if negOrPos*friendships[actor.name][victim.name]<negOrPos*event.baseProps["neededFriendLevelVictim"]["value"]:
            return (0, False)
        if "mutual" in event.baseProps and event.baseProps["mutual"]:
            if negOrPos*friendships[victim.name][actor.name]<negOrPos*event.baseProps["neededFriendLevel"]["value"]:
                return (0, False)
    if "loveRequiredVictim" in event.baseProps and event.baseProps["loveRequiredVictim"]:
        negOrPos = 1 if event.neededLoveLevelVictim["relation"] else -1
        if negOrPos*loveships[actor.name][victim.name]<negOrPos*event.baseProps["neededLoveLevelVictim"]["value"]:
            return (0, False)
        if "mutual" in event.baseProps and event.baseProps["mutual"]:
            if negOrPos*loveships[victim.name][actor.name]<negOrPos*event.baseProps["neededLoveLevel"]["value"]:
                return (0, False)
    friendlevel = friendships[actor.name][victim.name]
    lovelevel = loveships[actor.name][victim.name]
    if "mutual" in event.baseProps and event.baseProps["mutual"]:
        friendlevel = (friendlevel+friendships[victim.name][actor.name])/2
        lovelevel = (lovelevel+loveships[victim.name][actor.name])/2
    return(baseEventVictimWeight*
          (1+settings["relationInfluence"])**(friendlevel*event.baseProps["friendEffectVictim"])*
          (1+settings["relationInfluence"])**(lovelevel*event.baseProps["loveEffectVictim"]),
          True)
          
def onlyOneLeft(liveContestants, _):
    if len(liveContestants) == 1:
        return True
    return False