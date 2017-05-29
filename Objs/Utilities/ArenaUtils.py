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

def loggingStartup(state):
    state["callbackStore"]["eventLog"] = collections.defaultdict(partial(collections.defaultdict, partial(collections.defaultdict, str))) # Crazy nesting...
    state["callbackStore"]["killCounter"] = collections.defaultdict(int)
    state["callbackStore"]["contestantLog"] = collections.defaultdict(dict)

# Logs last event. Must be last callback in overrideContestantEvent. 
def logEventsByContestant(proceedAsUsual, eventOutputs, thisevent, mainActor, state, participants, victims, sponsorsHere):
    if proceedAsUsual:
        state["callbackStore"]["eventLog"][state["turnNumber"][0]][state["curPhase"]][mainActor.name] = thisevent.name
    else:
        state["callbackStore"]["eventLog"][state["turnNumber"][0]][state["curPhase"]][mainActor.name] = "overridden"
    
def logKills(proceedAsUsual, eventOutputs, thisevent, mainActor, state, participants, victims, sponsorsHere):
    if not eventOutputs[2] or (len(eventOutputs)<=3 and ("murder" not in thisevent.baseProps or not thisevent.baseProps["murder"])):
        return
    if len(eventOutputs)>3:
        killers = []
        if not eventOutputs[3]:
            trueKillDict = {}
        if isinstance(eventOutputs[3], dict):
            # if killers is a dict, handle this differently
            trueKillDict = eventOutputs[3]
    else:
        killers = [str(x) for x in set([mainActor]+participants+victims)]
        trueKillDict = {}
    if not (killers or trueKillDict):
        return
    trueKillCounterDict = {}
    for dead in eventOutputs[2]:
        if killers:
            # This dict uses relationship levels to give a weight to how likely it is that someone is the killer
            killDict = {x:1.1**(state["allRelationships"].friendships[str(x)][str(dead)]+2*state["allRelationships"].loveships[str(x)][str(dead)]) for x in killers if str(x)!=str(dead)}
            if not killDict: # This can happen if the only potential killer is also someone who died in the event.
                continue
            trueKiller = weightedDictRandom(killDict)[0]
            trueKillDict[str(dead)] = str(trueKiller)
        else:
            trueKiller = trueKillDict[str(dead)]
        if str(trueKiller) not in trueKillCounterDict:
            trueKillCounterDict[str(trueKiller)] = state["callbackStore"]["killCounter"][str(trueKiller)]
        state["callbackStore"]["killCounter"][str(trueKiller)] += 1
        state["callbackStore"]["KillThisTurnFlag"][str(trueKiller)] = True
        if str(trueKiller) != str(mainActor):
            # This is treated as if someone had done the worst possible thing to the dead person. There is also a stability impact.
            state["allRelationships"].IncreaseFriendLevel(state["contestants"][str(dead)], state["contestants"][str(trueKiller)], -10)
            state["allRelationships"].IncreaseLoveLevel(state["contestants"][str(dead)], state["contestants"][str(trueKiller)], -10)
        state["allRelationships"].KillImpact(dead)
        
    # Modify description to reflect kills
    killString = " [Kills: "
    killList = []
    for key, value in trueKillDict.items():
        trueKillCounterDict[value] += 1
        killList.append(value + " (" + str(trueKillCounterDict[value]) + ")" + " kills " + key)
    killString += ", ".join(killList) + "]"
    eventOutputs[0] += killString
        
def logContestants(liveContestants, baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, baseEventSponsorWeights, turnNumber, state):
    state["callbackStore"]["contestantLog"][turnNumber[0]] = liveContestants
    
def resetKillFlag(liveContestants, baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, baseEventSponsorWeights, turnNumber, state):
     state["callbackStore"]["KillThisTurnFlag"] = collections.defaultdict(dict)
        
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
    killWriter.finalWrite(os.path.join("Assets",str(state["turnNumber"][0])+" Kills.html"), state)
    return False

def sponsortTraitWrite(state):
    sponsorWriter =HTMLWriter()
    sponsorWriter.addTitle("Sponsor Traits")
    for sponsor in state["sponsors"].values():
        sponsorWriter.addEvent("Primary Trait: "+sponsor.primary_trait+"<br> Secondary Trait: "+sponsor.secondary_trait, [sponsor])
    sponsorWriter.finalWrite(os.path.join("Assets", "Sponsor Traits.html"), state)
    
def relationshipWrite(state):
    relationships = state["allRelationships"]
    firstTurn = ("relationshipLastTurn" not in state["callbackStore"])
    if not firstTurn:
        oldRelationshipsFriendships = state["callbackStore"]["relationshipLastTurn"]["friendships"]
        oldRelationshipsLoveships = state["callbackStore"]["relationshipLastTurn"]["loveships"]
    state["callbackStore"]["relationshipLastTurn"] = {}
    state["callbackStore"]["relationshipLastTurn"]["friendships"] = copy.deepcopy(relationships.friendships)
    state["callbackStore"]["relationshipLastTurn"]["loveships"] = copy.deepcopy(relationships.loveships)
    
    friendWriter = HTMLWriter()
    friendWriter.addTitle("Day "+str(state["turnNumber"][0])+" Friendships")
    loveWriter = HTMLWriter()
    loveWriter.addTitle("Day "+str(state["turnNumber"][0])+" Romances")
    anyEvent = next(iter(state["events"].values()))  # A hack to get around importing Events
    for person in list(state["contestants"].values())+list(state["sponsors"].values()):
        if not person.alive:
            continue
        friendLine = str(person)
        friendList = []
        lostFriendList = []
        enemyList = []
        lostEnemyList = []
        liveFriends = {x:y for x,y in relationships.friendships[str(person)].items() if x in state["contestants"] and state["contestants"][x].alive}
        sortFriends = {x:liveFriends[x] for x in sorted(liveFriends, key=liveFriends.get, reverse=True)}
        sortFriends.update({x:y for x,y in relationships.friendships[str(person)].items() if x in state["sponsors"]})
        for key, value in sortFriends.items():
            if value >= 4:
                writeString = key
                if not firstTurn:
                    if oldRelationshipsFriendships[str(person)][key] < 4:
                        writeString += ' (New!) '
                if relationships.friendships[key][str(person)] >=4:
                    friendList.append(writeString)
                else:
                    friendList.append(writeString+' (Not Mutual)')
            else:
                if not firstTurn:
                    if oldRelationshipsFriendships[str(person)][key] >=4:
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
                    enemyList.append(writeString+' (Not Mutual)')
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
        liveLoves = {x:y for x,y in relationships.loveships[str(person)].items() if x in state["contestants"] and state["contestants"][x].alive}
        sortLoves = {x:liveLoves[x] for x in sorted(liveLoves, key=liveLoves.get, reverse=True)}
        sortLoves.update({x:y for x,y in relationships.loveships[str(person)].items() if x in state["sponsors"]})
        for key, value in sortLoves.items():
            if value >= 4:
                writeString = key
                if not firstTurn:
                    if oldRelationshipsLoveships[str(person)][key] < 4:
                        writeString += ' (New!) '
                if relationships.loveships[key][str(person)] >=4:
                    loveList.append(writeString)
                else:
                    loveList.append(writeString+' (Not Mutual)')
            else:
                if not firstTurn:
                    if oldRelationshipsLoveships[str(person)][key] >=4:
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
                    loveEnemyList.append(writeString+' (Not Mutual)')
            else:
                if not firstTurn:
                    if oldRelationshipsLoveships[str(person)][key] <= -4:
                        tempString = key
                        if oldRelationshipsLoveships[key][str(person)] > -4:
                            tempString += ' (Not Mutual)'
                        lostLoveEnemyList.append(key)
        if loveList:
            loveLine +="<br> Romances: "
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

    friendWriter.finalWrite(os.path.join("Assets", str(state["turnNumber"][0])+" Friendships.html"), state)
    loveWriter.finalWrite(os.path.join("Assets", str(state["turnNumber"][0])+" Romances.html"), state)
    
# Rig it so the same event never happens twice to the same person in consecutive turns (makes game feel better)
def eventMayNotRepeat(actor, origProb, event, state):
    # in case a phase only has one event (special phases, among other things)
    if sum(1 for x in state['events'].values() if "phase" not in x.baseProps or state["curPhase"] in x.baseProps["phase"]) == 1:
        return origProb, True
    if state["turnNumber"][0]>1: # Since defaultdict, this would work fine even without this check, but this makes it more explicit (and is more robust to future changes)
        for x in state["callbackStore"]["eventLog"][state["turnNumber"][0]-1].values():
            if x[actor.name] == event.name: 
                return 0, False
    return origProb, True
  
# Ends the game if only one contestant left  
def onlyOneLeft(liveContestants, _):
    if len(liveContestants) == 1:
        return True
    return False