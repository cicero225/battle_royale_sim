"""The main for the battle royale sim"""

from __future__ import division # In case of Python 2+. The Python 3 implementation is way less dumb.


import copy
import json
import os
import random # A not very good random library, but probably fine for our purposes
import collections
# from functools import partial # Might be useful later

from Objs.Contestants.Contestant import Contestant, contestantIndivActorCallback, contestantIndivActorWithParticipantsCallback, contestantIndivActorWithVictimsCallback
from Objs.Items.Item import Item
from Objs.Sponsors.Sponsor import Sponsor
from Objs.World.World import World
from Objs.Relationships.Relationship import Relationship
import Objs.Utilities.ArenaUtils as ArenaUtils
from Objs.Events import *

def main():
    """The main for the battle royale sim"""
    
    # Initial Setup:

    # Import Settings from JSON -> going to make it a dictionarys
    with open('Settings.json') as settings_file:
        settings = json.load(settings_file)
 
    # List of settings as I come up with them. It can stay as a dict.
    # traitRandomness = 3
    # numContestants = 24 # Program should pad or randomly remove contestants as necessary
    # eventRandomness = 0.5 # Percent range over which the base weights of events varies from json settings
    # statInfluence = 0.3 # How much stats influence event weightings, calculated as (1+influence)^((stat-5)*eventInfluenceLevel)
    # objectInfluence = 1 # How much objects in inventory affect events. The default 1 uses the base stats.
    # relationInfluence = 0.1 # How much relationships affect event chance, calculated as (1+influence)^(relationship level*eventInfluenceLevel)
    # maxParticipantEffect = 3 # Maximum participants/victims can affect event probability. Arbitrary; there's no good way to estimate this.
    # Note that objects that fully disable a event should still do so!
    
    # TODO: Now that the item stats etc. are relatively set, should have the object loaders inspect the final dictionaries for correctness (no misspellings etc.) (since json doesn't have a mechanism for checking)
    
    # Initialize Events
    events = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Objs', 'Events', 'Events.json'), settings, Event.Event)
    eventsActive = {x: True for x in events} # Global array that permits absolute disabling of events regardless of anything else. This could also be done by directly setting the base weight to 0, but this is clearer.

    # Import and initialize contestants -> going to make it dictionary name : (imageName, baseStats...)
    contestants = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Objs', 'Contestants', 'Contestants.json'), settings, Contestant)
    # If number of contestants in settings less than those found in the json, randomly remove some
    contestantNames = contestants.keys()
    if settings['numContestants'] < len(contestantNames):
        contestantNames = random.sample(contestantNames, len(contestantNames)-settings['numContestants'])
        for remove in contestantNames:
            del contestants[remove]
    # If number of contestants in settings more than those found in the json, add Rando Calrissians
    for i in range(len(contestantNames), settings['numContestants']):
        # Here contestants[0].stats is used as a template for making random stats
        contestants['Rando Calrissian ' + str(i)] = Contestant.makeRandomContestant('Rando Calrissian ' + str(i), "M", "DUMMY_IMAGE", list(contestants.values())[0].stats, settings) # need Rando image to put here
        
    assert(len(contestants)==settings['numContestants'])
    
    for contestant in contestants.values():
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
    
    state = {
    "contestants": contestants,
    "sponsors": sponsors,
    "events": events,
    "eventsActive": eventsActive,
    "items": items,
    "arena": arena,
    "allRelationships": allRelationships,
    "turnNumber": turnNumber,
    "callbackStore": callbackStore,
    } # Allows for convenient passing of the entire game state to anything that needs it (usually events)
    
    # CALLBACKS
    # As much as possible influence event processing from here. Note that these callbacks happen IN ORDER. It would be possible to do this in a more
    # modular manner by defining a callback object, defining a registering function, using decorators... but that provides effectively no control on
    # the order of operation. For now, it is better to just have it like this.
    
    # Also, for now, relationship callbacks are in ArenaUtils
    
    # modifyBaseWeights: Expected args: baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, turnNumber. Modify in place.
        # Also a good time to do any beginning of turn stuff
    modifyBaseWeights = []    
    # modifyIndivActorWeights: Expected args: actor, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
    modifyIndivActorWeights = [
    contestantIndivActorCallback,
    allRelationships.relationsMainWeightCallback
    ]
    # modifyIndivActorWeightsWithParticipants: Expected args: actor, participant, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
    modifyIndivActorWeightsWithParticipants = [
    contestantIndivActorWithParticipantsCallback,
    allRelationships.relationsParticipantWeightCallback
    ]
    # modifyIndivActorWeightsWithVictims: Expected args: actor, victim, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
    modifyIndivActorWeightsWithVictims = [
    contestantIndivActorWithVictimsCallback,
    allRelationships.relationsVictimWeightCallback
    ]
    # In case it ever becomes a good idea to directly manipulate events as they happen. Expected args: contestantName, eventName, state. Return: bool proceedAsUsual (True if you want the usual event chain to still happen)
    # Note that if *any* of these returns false, then normal event processing is overridden
    overrideContestantEvent = []  
    # Conditions for ending the game. Expected args: liveContestants, state. Return: bool endGame. (True if you want game to end)
    endGameConditions = [
    ArenaUtils.onlyOneLeft
    ]
    
    callbacks = {"modifyBaseWeights": modifyBaseWeights,
                 "modifyIndivActorWeights": modifyIndivActorWeights,
                 "modifyIndivActorWeightsWithParticipants": modifyIndivActorWeightsWithParticipants,
                 "modifyIndivActorWeightsWithVictims": modifyIndivActorWeightsWithVictims,
                 "overrideContestantEvent": overrideContestantEvent,
                 "endGameConditions": endGameConditions,
    }
    state["callbacks"] = callbacks # I define state before callbacks so it can be bound to a callback if necessary
    
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
    # Main loop of DEATH
    lastEvents = {}
    while True:
        if not restartTurn:
            turnNumber[0] += 1
            print("Day "+str(turnNumber[0]))
        restartTurn = False # If set to true, this runs end of turn processing. Otherwise it reloops immediately. Only used if turn is reset.
        initialState = copy.deepcopy(state) #Obviously very klunky and memory-intensive, but only clean way to allow resets under the current paradism. The other option is to force the last event in a turn to never kill the last contestant.
        liveContestants = {x: y for x, y in contestants.items() if y.alive}
        # Sample contestants randomly
        randOrderContestantKeys = random.sample(liveContestants.keys(), len(liveContestants))
        # Get base event weights (now is the time to shove in the effects of any special turn, whenever that gets implemented)
        baseEventActorWeights = {x: y.baseProps["mainWeight"] if eventsActive[x] else 0 for x, y in events.items()}
        baseEventParticipantWeights = {x: y.baseProps["participantWeight"] for x, y in events.items() if "participantWeight" in y.baseProps}
        baseEventVictimWeights = {x: y.baseProps["victimWeight"] for x, y in events.items() if "victimWeight" in y.baseProps}
        #Do callbacks for modifying base weights
        for callback in callbacks["modifyBaseWeights"]:
            callback(baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, turnNumber)
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
            for eventName, event in events.items():
                indivProb[eventName] = baseEventActorWeights[eventName]
                if contestantKey in lastEvents and lastEvents[contestantKey] == eventName: # Rig it so the same event never happens twice to the same person (makes game feel better)
                    indivProb[eventName] = 0
                    continue
                eventMayProceed = True
                for callback in callbacks["modifyIndivActorWeights"]:
                    indivProb[eventName], eventMayProceed = callback(actor, indivProb[eventName], event)
                    if not eventMayProceed: # If one returns false, it signals that the event has been blocked
                        break
                if not eventMayProceed:
                    continue
                origIndivWeight = indivProb[eventName]
                # Probability correction for multi-contestant events, if necessary
                if eventName in baseEventParticipantWeights:
                    # A bit of set magic
                    validParticipants = set(liveContestants) - alreadyUsed
                    for x in validParticipants:
                        try:
                            validParticipants.difference_update(contestants[x].eventDisabled[eventName]["participant"])
                        except:
                            pass
                    if len(validParticipants) < event.baseProps["numParticipants"]:
                        indivProb[eventName] = 0 # This event cannot happen
                        continue
                    for participant in validParticipants:
                        eventParticipantWeights[eventName][participant] = baseEventParticipantWeights[eventName]
                        eventMayProceed = True
                        for callback in callbacks["modifyIndivActorWeightsWithParticipants"]:
                            eventParticipantWeights[eventName][participant], eventMayProceed = callback(actor, contestants[participant],
                                                                                                        eventParticipantWeights[eventName][participant],
                                                                                                        event)
                            if not eventMayProceed:
                                break
                    correctionParticipantWeight = sum(eventParticipantWeights[eventName].values())/len(eventParticipantWeights)
                    indivProb[eventName] *= min(correctionParticipantWeight/origIndivWeight, settings["maxParticipantEffect"])
                if eventName in baseEventVictimWeights:
                    # A bit of set magic
                    validVictims = set(liveContestants) - alreadyUsed
                    for x in validVictims:
                        try:
                            validVictims.difference_update(contestants[x].eventDisabled[eventName]["victim"])
                        except:
                            pass
                    if len(validVictims) < event.baseProps["numVictims"]:
                        indivProb[eventName] = 0 # This event cannot happen
                        continue
                    for victim in validVictims:
                        eventVictimWeights[eventName][victim] = baseEventVictimWeights[eventName]
                        eventMayProceed = True
                        for callback in callbacks["modifyIndivActorWeightsWithVictims"]:
                            eventVictimWeights[eventName][victim], eventMayProceed = callback(actor, contestants[victim],
                                                                                                        eventVictimWeights[eventName][victim],
                                                                                                        event)
                            if not eventMayProceed:
                                break
                    correctionVictimWeight = sum(eventVictimWeights[eventName].values())/len(eventVictimWeights)
                    indivProb[eventName] *= min(correctionVictimWeight/origIndivWeight, settings["maxParticipantEffect"])
            
            #Now select which event happens and make it happen, selecting additional participants and victims by the relative chance they have of being involved.
            eventName = ArenaUtils.weightedDictRandom(indivProb)[0]
            # Handle event overrides, if any
            proceedAsUsual = True
            for override in callbacks["overrideContestantEvent"]:
                proceedAsUsual = override(contestantKey, eventName, state) and proceedAsUsual # Because of short-circuit processing, the order here is important
            if proceedAsUsual:
                #Determine participants, victims, if any.
                thisevent = events[eventName]
                if eventName in baseEventParticipantWeights:
                    participantkeys = ArenaUtils.weightedDictRandom(eventParticipantWeights[eventName], thisevent.baseProps["numParticipants"])
                    try:
                        participants = [contestants[key] for key in participantkeys]
                    except KeyError:
                        participants = [contestants[participantkeys]]
                else:
                    participants = []
                if eventName in baseEventVictimWeights:
                    victimkeys = ArenaUtils.weightedDictRandom(eventVictimWeights[eventName], thisevent.baseProps["numVictims"])
                    try:
                        victims = [contestants[key] for key in victimkeys]
                    except KeyError:
                        victims = [contestants[victimkeys]]
                else:
                    victims = []
                lastEvents[contestantKey] = eventName
                desc, descContestants, theDead = thisevent.doEvent(contestants[contestantKey], state, participants, victims)
                
            # TODO: Placeholder. Probably want object or specialist function for this later.
            print(desc)
            
            #Check if everyone is now dead...
            if all(not x.alive for x in liveContestants.values()):
                # This turn needs to be rerun
                for key, element in initialState.items(): # This is careful use of how python passing works. The values of state now point to the memory references of those in initialState.
                # On the next loop, initialState will be overwritten by copy.deepcopy(state), but the references in state will still point to the right places and won't be released. 
                    state[key] = element
                restartTurn = True
                break
            
            # Remove the dead contestants from the live list. Add the contestants involved to alreadyUsed.
            for dead in theDead:
                del liveContestants[dead]
            alreadyUsed.update(descContestants) 
        
        if not restartTurn:    
            for callback in callbacks["endGameConditions"]: # conditions for ending the game
                if callback(liveContestants, state):
                    # TODO: Placeholder under I decide what to do with this later
                    print(list(liveContestants.values())[0].name + " survive(s) the game and win(s)!")
                    # TODO: Do any additional end of simulation stuff here
                    return
            
if __name__ == "__main__":
    main()
