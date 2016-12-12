"""Utility functions for battle royale sim"""
import json
import random
import bisect

    
def weightedDictRandom(inDict, num_sel=1):
    """Given an input dictionary with weights as values, picks num_sel uniformly weighted random selection from the keys"""
    if num_sel > len(inDict):
        raise IndexError
    def getKeysDirect(inDict, num_direct):
        if not num_direct:
            return []
        keys = []
        allkeys = list(inDict.keys())
        allvalues = list(inDict.values())
        cumsum = [0]
        for weight in allvalues:  # itervalues is better practice in python 2.x, but doesn't exist in 3...
            cumsum.append(cumsum[-1]+weight)
        for dummy in range(num_direct):
            thisrand = random.uniform(1e-100,cumsum[-1]-1e-100) #The 1e-100 is important for numerical reasons
            selected = bisect.bisect_left(cumsum,thisrand)-1
            keys.append(allkeys.pop(selected))
            if dummy != num_direct-1:
                remWeight = allvalues.pop(selected)
                for x in range(selected+1,len(cumsum)):
                    cumsum[x] -= remWeight
        return keys
    if num_sel < len(inDict)/2:
        return tuple(getKeysDirect(inDict, num_sel))
    else:
        return tuple(set(inDict.keys()).difference(getKeysDirect(inDict,len(inDict)-num_sel)))
            
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
    if event.mainFriendEffect:
        negOrPos = 1 if event.mainNeededFriendLevel["relation"] else -1
        for friendLevel in friendships[actor.name].itervalues():
            if negOrPos*friendLevel >= event.mainNeededFriendLevel["value"]:
                baseEventActorWeight *= (1+settings["relationInfluence"])**event.mainFriendEffect
                break
    if event.mainLoveEffect:
        negOrPos = 1 if event.mainNeededLoveLevel["relation"] else -1
        for loveLevel in loveships[actor.name].itervalues():
            if negOrPos*loveLevel >= event.mainNeededLoveLevel["value"]:
                baseEventActorWeight *= (1+settings["relationInfluence"])**event.mainLoveEffect
                break
    return (baseEventActorWeight, True)

    
def relationsParticipantWeightCallback(friendships, loveships, settings, actor, participant, baseEventParticipantWeight, event):
    if event.friendRequired: #This will need an additional check later in case of multi-friend events
        negOrPos = 1 if event.neededFriendLevel["relation"] else -1
        if negOrPos*friendships[actor.name][participant.name]<negOrPos*event.neededFriendLevel["value"]:
            return (0, False)
    if event.loveRequired: #This will need an additional check later in case of multi-friend events
        negOrPos = 1 if event.neededLoveLevel["relation"] else -1
        if negOrPos*loveships[actor.name][participant.name]<negOrPos*event.neededLoveLevel["value"]:
            return (0, False)
    return(baseEventParticipantWeight*
          (1+settings["relationInfluence"])**(friendships[actor.name][participant.name]*event.friendEffect)*
          (1+settings["relationInfluence"])**(loveships[actor.name][participant.name]*event.loveEffect),
          True)
 
 
def relationsVictimWeightCallback(friendships, loveships, settings, actor, victim, baseEventVictimWeight, event):
    if event.friendRequired: #This will need an additional check later in case of multi-friend events
        negOrPos = 1 if event.neededFriendLevel["relation"] else -1
        if negOrPos*friendships[actor.name][victim.name]<negOrPos*event.neededFriendLevel["value"]:
            return (0, False)
    if event.loveRequired: #This will need an additional check later in case of multi-friend events
        negOrPos = 1 if event.neededLoveLevel["relation"] else -1
        if negOrPos*loveships[actor.name][victim.name]<negOrPos*event.neededLoveLevel["value"]:
            return (0, False)
    return(baseEventVictimWeight*
          (1+settings["relationInfluence"])**(friendships[actor.name][victim.name]*event.friendEffect)*
          (1+settings["relationInfluence"])**(loveships[actor.name][victim.name]*event.loveEffect),
          True)
          
def onlyOneLeft(liveContestants, _):
    if len(liveContestants) == 1:
        return True
    return False