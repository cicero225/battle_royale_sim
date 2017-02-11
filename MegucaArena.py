"""The main for the battle royale sim"""

from __future__ import division # In case of Python 2+. The Python 3 implementation is way less dumb.

import sys
import copy
import json
import os
import random # A not very good random library, but probably fine for our purposes
import statistics # Note: this is Python 3.4 +
import collections
from functools import partial # Might be useful later
import traceback

from Objs.Contestants.Contestant import Contestant, contestantIndivActorCallback, contestantIndivActorWithParticipantsCallback, contestantIndivActorWithVictimsCallback
from Objs.Items.Item import Item
from Objs.Sponsors.Sponsor import Sponsor, contestantIndivActorWithSponsorsCallback
from Objs.World.World import World
from Objs.Relationships.Relationship import Relationship
import Objs.Utilities.ArenaUtils as ArenaUtils
from Objs.Events import *
from Objs.Display.HTMLWriter import HTMLWriter

PRINTHTML = True
DEBUG = True
STATSDEBUG = {}

def main():
    """The main for the battle royale sim"""
    
    # Initial Setup:

    # State initialization. This should NEVER EVER be reassigned.
    state = {}
    
    # Import Settings from JSON -> going to make it a dictionarys
    with open('Settings.json') as settings_file:
        settings = json.load(settings_file)
        
    with open('Phases.json') as phases_file:
        phases = json.load(phases_file)
 
    # List of settings as I come up with them. It can stay as a dict.
    # traitRandomness = 3
    # numContestants = 24 # Program should pad or randomly remove contestants as necessary
    # eventRandomness = 0.5 # Percent range over which the base weights of events varies from json settings
    # statInfluence = 0.3 # How much stats influence event weightings, calculated as (1+influence)^((stat-5)*eventInfluenceLevel)
    # objectInfluence = 1 # How much objects in inventory affect events. The default 1 uses the base stats.
    # relationInfluence = 0.1 # How much relationships affect event chance, calculated as (1+influence)^(relationship level*eventInfluenceLevel)
    # maxParticipantEffect = 3 # Maximum participants/victims can affect event probability. Arbitrary; there's no good way to estimate this.
    # statFriendEffect = 0.5 # How much stats such as friendliness affect rate of relationship change
    # friendCombatEffect = 0.5 # How much friends/lovers help in combat
    # combatAbilityEffect = 0.3 # How much combat ability (and associated modifiers) affect chance of death in combat. i.e. 0 would make it pure random
    # Note that objects that fully disable a event should still do so!
    
    # TODO: Now that the item stats etc. are relatively set, should have the object loaders inspect the final dictionaries for correctness (no misspellings etc.) (since json doesn't have a mechanism for checking)
    
    # Initialize Events
    # Ugly, but oh well.
    Event.Event.stateStore[0] = state
    events = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Objs', 'Events', 'Events.json'), settings, Event.Event)
    eventsActive = {x: True for x in events} # Global array that permits absolute disabling of events regardless of anything else. This could also be done by directly setting the base weight to 0, but this is clearer.

    # Import and initialize contestants -> going to make it dictionary name : (imageName, baseStats...)
    contestants = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Objs', 'Contestants', 'Contestants.json'), settings, Contestant)
    if not settings['matchContestantCount']:
        # If number of contestants in settings less than those found in the json, randomly remove some
        contestantNames = contestants.keys()
        if settings['numContestants'] < len(contestantNames):
            contestantNames = random.sample(contestantNames, len(contestantNames)-settings['numContestants'])
            for remove in contestantNames:
                del contestants[remove]
        # If number of contestants in settings more than those found in the json, add Rando Calrissians
        for i in range(len(contestantNames), settings['numContestants']):
            # Here contestants[0].stats is used as a template for making random stats
            contestants['Rando Calrissian ' + str(i)] = Contestant.makeRandomContestant('Rando Calrissian ' + str(i), "M", "Rando.jpg", list(contestants.values())[0].stats, settings) # need Rando image to put here
        
        assert(len(contestants)==settings['numContestants'])
    else:
        settings['numContestants'] = len(contestants)
    
    if settings["statNormalization"]:
        targetSum = sum(sum(x.stats.values()) for x in contestants.values())/len(contestants)
    for contestant in contestants.values():
        if settings["statNormalization"]:
            contestant.contestantStatNormalizer(targetSum)
        contestant.InitializeEventModifiers(events)

    # Import and initialize sponsors -> going to make it dictionary name : (imageName,baseStats...)
    # baseStats =  weight (probability relative to other sponsors, default 1), objectPrefs (any biases towards or away any \
    # from any type of object gift, otherwise 1, Anything else we think of)
    # No placeholder sponsors because of the way it is handled.
    sponsors = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Objs', 'Sponsors', 'Sponsors.json'), settings, Sponsor)

    # for now relationship levels (arbitrarily, -5 to 5, starting at zero) are stored in this dict. Later on we can make relationship objects to store, if this is somehow useful.
    allRelationships = Relationship(contestants, sponsors, settings)


    # Import and initialize Items -> going to make it dictionary name : (imageName,baseStats...)
    items = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Objs', 'Items', 'Items.json'), settings, Item)

    # Initialize World - Maybe it should have its own settings?
    arena = World(settings) #Maybe other arguments in future, i.e. maybe in an extended world items can be found on the ground, but leaving this as-is for now.
    
    turnNumber = [0] # Deliberately a list of 1, so it's passed by reference
    
    callbackStore = {} #Arbitrary storage specifically for non-main objects/callbacks to use. Make sure to use a unique key (ideally involving the name of the function)
    
    thisWriter = None # current HTML display object
    
    state.update({
    "settings": settings,
    "contestants": contestants,
    "sponsors": sponsors,
    "events": events,
    "eventsActive": eventsActive,
    "items": items,
    "arena": arena,
    "allRelationships": allRelationships,
    "turnNumber": turnNumber,
    "callbackStore": callbackStore,
    "thisWriter": thisWriter,
    "phases": phases
    }) # Allows for convenient passing of the entire game state to anything that needs it (usually events)
    
    # CALLBACKS
    # As much as possible influence event processing from here. Note that these callbacks happen IN ORDER. It would be possible to do this in a more
    # modular manner by defining a callback object, defining a registering function, using decorators... but that provides effectively no control on
    # the order of operation. For now, it is better to just have it like this.
    
    # Also, for now, relationship callbacks are in ArenaUtils
    
    # Run once before the start of the game. Expected args: state. Modify in place.
    startup = [
    ArenaUtils.loggingStartup,]
    
    # modifyBaseWeights: Expected args: liveContestants, baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, baseEventSponsorWeights, turnNumber, state. Modify in place.
        # Also a good time to do any beginning of turn stuff
    modifyBaseWeights = [
    ArenaUtils.logContestants]
    
    # modifyIndivActorWeights: Expected args: actor, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
    modifyIndivActorWeights = [
    partial(ArenaUtils.eventMayNotRepeat, state=state),
    contestantIndivActorCallback,
    allRelationships.relationsMainWeightCallback
    ]
    # modifyIndivActorWeightsWithParticipants: Expected args: actor, participant, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
    modifyIndivActorWeightsWithParticipants = [
    contestantIndivActorWithParticipantsCallback,
    partial(allRelationships.relationsRoleWeightCallback, "Participant")
    ]
    # modifyIndivActorWeightsWithVictims: Expected args: actor, victim, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
    modifyIndivActorWeightsWithVictims = [
    contestantIndivActorWithVictimsCallback,
    partial(allRelationships.relationsRoleWeightCallback, "Victim")
    ]
    
    # modifyIndivActorWeightsWithSponsors: Expected args: actor, sponsor, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
    modifyIndivActorWeightsWithSponsors = [
    contestantIndivActorWithSponsorsCallback,
    partial(allRelationships.relationsRoleWeightCallback, "Sponsor")
    ]
    
    # In case it ever becomes a good idea to directly manipulate events as they happen. Expected args: contestantKey, thisevent, state, participants, victims, sponsorsHere. Return: bool proceedAsUsual, resetEvent (True if you want the usual event chain to still happen, and True if you want the event to Reset entirely)
    # Note that if *any* of these returns "unusually", then normal event processing is overridden and no further callbacks occur
    overrideContestantEvent = []  
    
    # Things that happen after event processing (usually logging or emergency reset. Note that resetting callbacks need to happen before logging.
    # Expected args: proceedAsUsual, eventOutputs, thisevent, contestants[contestantKey], state, participants, victims, sponsorsHere
    postEventCallbacks = [
        ArenaUtils.logEventsByContestant,
        ArenaUtils.logKills
    ]
    # Conditions for ending the game. Expected args: liveContestants, state. Return: bool endGame. (True if you want game to end)
    endGameConditions = [
    ArenaUtils.onlyOneLeft
    ]
    
    postDayCallbacks = [ # Things that happen after each day
    ArenaUtils.endHypothermiaIfDayHasPassed
    ]
    
    if PRINTHTML:
        postDayCallbacks.insert(0, ArenaUtils.killWrite)
    
    callbacks = {"startup": startup,
                 "modifyBaseWeights": modifyBaseWeights,
                 "modifyIndivActorWeights": modifyIndivActorWeights,
                 "modifyIndivActorWeightsWithParticipants": modifyIndivActorWeightsWithParticipants,
                 "modifyIndivActorWeightsWithVictims": modifyIndivActorWeightsWithVictims,
                 "modifyIndivActorWeightsWithSponsors": modifyIndivActorWeightsWithSponsors,
                 "overrideContestantEvent": overrideContestantEvent,
                 "postEventCallbacks": postEventCallbacks,
                 "endGameConditions": endGameConditions,
                 "postDayCallbacks": postDayCallbacks
    }
    
    # loophole that allows event-defining files to slip callbacks in
    for store, funcList in Event.Event.inserted_callbacks.items():
        callbacks[store].extend(funcList)
    
    state["callbacks"] = callbacks
    
    # Nested functions that need access to variables in main
    
    def modifyWeightForMultipleActors(trueNumRoles, baseWeights, weights, roleName, numRoles, callbackName, people=contestants, forSponsors=False):
        trueNumRoles[eventName] = 0
        if eventName in baseWeights:
            trueNumRoles[eventName] = event.baseProps[numRoles]+(random.randint(0, event.baseProps[numRoles+"Extra"]) if numRoles+"Extra" in event.baseProps else 0)
            if not trueNumRoles[eventName]:
                return
            if not origIndivWeight: # this causes numerical issues and shoudl end up 0 anyway
                indivProb[eventName] = 0.0
                return
            # A bit of set magic
            if forSponsors:
                validRoles = people.keys()
            else:
                validRoles = set(liveContestants) - alreadyUsed
                for x in validRoles:
                    try:
                        validRoles.difference_update(people[x].eventDisabled[eventName][roleName])
                    except:
                        pass
                if len(validRoles) < trueNumRoles[eventName]:
                    indivProb[eventName] = 0 # This event cannot happen
                    return
            for role in validRoles:
                weights[eventName][role] = baseWeights[eventName]
                eventMayProceed = True
                for callback in callbacks[callbackName]:
                    weights[eventName][role], eventMayProceed = callback(actor, people[role],
                                                                         weights[eventName][role],
                                                                         event)
                    if not eventMayProceed:
                        break            
            if sum(bool(x) for x in weights[eventName].values())<trueNumRoles[eventName]:
                indivProb[eventName] = 0
                return
            correctionRoleWeight = sum(weights[eventName].values())/len(weights)
            indivProb[eventName] *= min(correctionRoleWeight/origIndivWeight, settings["maxParticipantEffect"])
            
    def selectRoles(baseWeights, weights, trueNumRoles, people=contestants):
        if eventName in baseWeights and trueNumRoles[eventName]>0:
            rolekeys = ArenaUtils.weightedDictRandom(weights[eventName], trueNumRoles[eventName])
            try:
                roles = [people[key] for key in rolekeys]
            except KeyError:
                roles = [people[rolekeys]]
        else:
            roles = []
        return roles
    
    # Run simulation

    # General idea:
    # Sample contestants randomly
    # Go through contestants
    # For each contestant, go through event list and poll their weights + contestant weight modifiers (base weights + object and relationship modifiers)
    # (Remember that base event weights may change based on turn)
    # (For multi-contestant events, there should also be a weight stored for a) being a "participant" on the side of whoever started the event and b) being a "victim"
    # These should affect the final weight used (I should figure out a formula for this) and also be used to pick secondary participants/victims.
    # Using these weights, pick an event and call its method. If multi-contestant, also make sure not to let them roll another event.
    # Check that this turn has not killed everyone. If it has, redo the _entire_ turn (it's the only fair way).
    # Then print results into HTML (?) or whatever makes sense
    # Repeat.
    restartTurn = False
    
    #Startup callbacks
    for callback in callbacks["startup"]:
        callback(state)
        
    # Main loop of DEATH
    lastEvents = {}
    while True:
        turnNumber[0] += 1
        if turnNumber[0] in phases:
            thisDay = phases[turnNumber[0]]
        else:
            thisDay = phases["default"]
        print("Day "+str(turnNumber[0]))
        for phaseNum, thisPhase in enumerate(thisDay["phases"]):
            titleString = thisDay["titles"][phaseNum]
            state["curPhase"] = thisPhase
            eventsActive = {eventName: True for eventName, x in events.items() if "phase" not in x.baseProps or thisPhase in x.baseProps["phase"]}
            while True: # this just allows resetting the iteration
                if PRINTHTML:
                    thisWriter = HTMLWriter()
                    thisWriter.addTitle(titleString.replace('#', str(turnNumber[0])))
                restartTurn = False # If set to true, this runs end of turn processing. Otherwise it reloops immediately. Only used if turn is reset.
                initialState = copy.deepcopy(state) #Obviously very klunky and memory-intensive, but only clean way to allow resets under the current paradism. The other option is to force the last event in a turn to never kill the last contestant.
                liveContestants = {x: y for x, y in contestants.items() if y.alive}
                if phaseNum == 0: # I want to be explicit here
                    origLiveContestants = copy.copy(liveContestants)
                # Sample contestants randomly
                randOrderContestantKeys = random.sample(liveContestants.keys(), len(liveContestants))
                # Get base event weights (now is the time to shove in the effects of any special turn, whenever that gets implemented)
                baseEventActorWeights = {x: y.baseProps["mainWeight"] if x in eventsActive and eventsActive[x] else 0 for x, y in events.items()}
                baseEventParticipantWeights = {x: y.baseProps["participantWeight"] for x, y in events.items() if "participantWeight" in y.baseProps}
                baseEventVictimWeights = {x: y.baseProps["victimWeight"] for x, y in events.items() if "victimWeight" in y.baseProps}
                baseEventSponsorWeights = {x: y.baseProps["sponsorWeight"] for x, y in events.items() if "sponsorWeight" in y.baseProps}
                #Do callbacks for modifying base weights
                for callback in callbacks["modifyBaseWeights"]:
                    callback(liveContestants, baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, baseEventSponsorWeights, turnNumber, state)
                # Now go through the contestants and trigger events based on their individualized probabilities
                alreadyUsed = set()
                for contestantKey in randOrderContestantKeys: #This is not statistically uniform because these multi-person events are hard and probably not worth figuring out in exact detail...
                    if contestantKey in alreadyUsed:
                        continue
                    actor = liveContestants[contestantKey] # Some contestants may die in events, they get removed at the end of the for loop
                    alreadyUsed.add(contestantKey) 
                    # Calculate individualized/multi-contestant corrected event probabilities
                    indivProb = {}
                    eventParticipantWeights = collections.defaultdict(dict) # We're about to calculate it here, and we don't want to recalculate when we get to the *next* for loop, so let's save it
                    eventVictimWeights = collections.defaultdict(dict) # We're about to calculate it here, and we don't want to recalculate when we get to the *next* for loop, so let's save it
                    eventSponsorWeights = collections.defaultdict(dict) # We're about to calculate it here, and we don't want to recalculate when we get to the *next* for loop, so let's save it
                    trueNumParticipants = {}
                    trueNumVictims = {}
                    trueNumSponsors = {}
                    for eventName, event in events.items():
                        indivProb[eventName] = baseEventActorWeights[eventName]                
                        eventMayProceed = True
                        for callback in callbacks["modifyIndivActorWeights"]:
                            indivProb[eventName], eventMayProceed = callback(actor, indivProb[eventName], event)
                            if not eventMayProceed: # If one returns false, it signals that the event has been blocked
                                break
                        if not eventMayProceed:
                            continue
                        origIndivWeight = indivProb[eventName]
                        # Probability correction for multi-contestant events, if necessary
                        # this feels silly but is very useful
                        modifyWeightForMultipleActors(trueNumParticipants, baseEventParticipantWeights, eventParticipantWeights, "participant", "numParticipants", "modifyIndivActorWeightsWithParticipants")
                        modifyWeightForMultipleActors(trueNumVictims, baseEventVictimWeights, eventVictimWeights, "victim", "numVictims", "modifyIndivActorWeightsWithVictims")
                        modifyWeightForMultipleActors(trueNumSponsors, baseEventSponsorWeights, eventSponsorWeights, "sponsor", "numSponsors", "modifyIndivActorWeightsWithSponsors", sponsors, True)
                    # It is occasionally useful for an event to be able to force a new event to be chosen.
                    # While computationally wasteful, this prevents us from needing to make a special callback for
                    # events with unique trigger conditions. Events may signal for a reselection by returning None or []
                    # Note, however, that this _not_ a good way to enforce specific participants, etc. as this is both wasteful
                    # and not-statistically accurate.
                    while(True):
                        #Now select which event happens and make it happen, selecting additional participants and victims by the relative chance they have of being involved. 
                        eventName = ArenaUtils.weightedDictRandom(indivProb)[0]     
                        if DEBUG:
                           STATSDEBUG["state"] = state
                           STATSDEBUG["indivProb"] = indivProb
                        # Handle event overrides, if any
                        #Determine participants, victims, if any.
                        thisevent = events[eventName]
                        participants = selectRoles(baseEventParticipantWeights, eventParticipantWeights, trueNumParticipants)
                        victims = selectRoles(baseEventVictimWeights, eventVictimWeights, trueNumVictims)
                        sponsorsHere = selectRoles(baseEventSponsorWeights, eventSponsorWeights, trueNumSponsors, sponsors)
                        proceedAsUsual = True
                        resetEvent = False
                        for override in callbacks["overrideContestantEvent"]:
                            # Be very careful of modifying state here.
                            proceedAsUsual, resetEvent = override(contestantKey, thisevent, state, participants, victims, sponsorsHere)
                            if not proceedAsUsual or resetEvent:
                                break
                        if resetEvent:
                            continue
                        if proceedAsUsual:
                            eventOutputs = thisevent.doEvent(contestants[contestantKey], state, participants, victims, sponsorsHere)
                            if not eventOutputs:
                                indivProb[eventName] = 0 # Apparently this event is not valid for this contestant (participants etc. should not be considered)
                                continue
                            desc, descContestants, theDead = eventOutputs[:3]
                        for postEvent in callbacks["postEventCallbacks"]:
                            postEvent(proceedAsUsual, eventOutputs, thisevent, contestants[contestantKey], state, participants, victims, sponsorsHere)
                        break
                    
                    print(eventName)
                    if PRINTHTML:
                        thisWriter.addEvent(desc, descContestants)
                    else:
                        print(desc)
                    
                    #Check if everyone is now dead...
                    if all(not x.alive for x in liveContestants.values()):
                        # This turn needs to be rerun
                        state.clear()
                        state.update(initialState.copy())
                        settings = state['settings']
                        contestants = state['contestants']
                        callbacks = state['callbacks']
                        sponsors = state['sponsors']
                        events = state['events']
                        eventsActive = state['eventsActive']
                        items = state['items']
                        arena = state['arena']
                        allRelationships = state['allRelationships']
                        turnNumber = state['turnNumber']
                        callbackStore = state['callbackStore']
                        thisWriter = state['thisWriter']
                        Event.stateStore = state
                        restartTurn = True
                        break
                    
                    # Remove the dead contestants from the live list. Add the contestants involved to alreadyUsed.
                    for dead in theDead:
                        del liveContestants[dead]
                    alreadyUsed.update([x.name for x in descContestants])   
            
                if not restartTurn:    
                    for callback in callbacks["endGameConditions"]: # conditions for ending the game
                        if callback(liveContestants, state):
                            if PRINTHTML:
                                thisWriter.addBigLine(list(liveContestants.values())[0].name + " survive(s) the game and win(s)!")
                                thisWriter.finalWrite(os.path.join("Assets", str(turnNumber[0])+" Phase "+thisPhase+".html"))
                            else:
                                print(list(liveContestants.values())[0].name + " survive(s) the game and win(s)!")

                            # TODO: Do any additional end of simulation stuff here
                            return list(liveContestants.values())[0].name, turnNumber[0]
                    if PRINTHTML:
                        if phaseNum == len(thisDay["phases"])-1:
                            deadThisTurn = set(origLiveContestants.values()) - set(liveContestants.values())
                            if deadThisTurn:
                                thisWriter.addEvent("The following names were added to the memorial wall: "+Event.Event.englishList(deadThisTurn), deadThisTurn)
                        thisWriter.finalWrite(os.path.join("Assets", str(turnNumber[0])+" Phase "+thisPhase+".html"))
                    break
        for callback in callbacks["postDayCallbacks"]:
            callback(state)  
        if turnNumber[0]>200:
            raise TooManyDays('Way too many days')

class TooManyDays(Exception):
    pass
            
def statCollection(): # expand to count number of days, and fun stuff like epiphany targets?
    statDict = collections.defaultdict(int)
    numErrors = 0
    days = []
    global PRINTHTML
    PRINTHTML = False
    for _ in range(0,1000):
        printtrace = True
        try:
            winner, day = main()
            statDict[winner] += 1
            days.append(day)
        except TooManyDays:
            pass
        except Exception as e:
            if not DEBUG:
                numErrors +=1
            else:
                if printtrace:
                    traceback.print_exc()
                    printtrace = False
                while True:
                    y = input()
                    if y.lower() == "q":
                        break
                    try:
                        eval('print('+y+')')
                    except Exception as e2:
                        print(e2)
    print(statDict)
    print(sum(days)/len(days))
    print(statistics.stdev(days))
    print(numErrors)

if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1] == '--stats':
        statCollection()
    else:
        main()