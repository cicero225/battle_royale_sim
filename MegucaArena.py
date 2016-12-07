"""The main for the battle royale sim"""

import json
import os
import random # A not very good random library, but probably fine for our purposes
import itertools
from functools import partial

from __future__ import division # In case of Python 2+. The Python 3 implementation is way less dumb.

from Contestants.Contestant import *
from Items.Item import Item
from Sponsors.Sponsor import Sponsor
from World.World import World
import ArenaUtils
import Events

def main():
    """The main for the battle royale sim"""
    
    # Initial Setup:

    # Import Settings from JSON -> going to make it a dictionary
    with open('Settings.json') as settings_file:
        settings = json.load(settings_file)

    # List of settings as I come up with them. It can stay as a dict.
    # traitRandomness = 3
    # numContestants = 24 # Program should pad or randomly remove contestants as necessary
    # eventRandomness = 0.5 # Percent range over which the base weights of events varies from json settings
    # statInfluence = 0.3 # How much stats influence event weightings, calculated as (1+influence)^((stat-5)*eventInfluenceLevel)
    # objectInfluence = 1 # How much objects in inventory affect events. The default 1 uses the base stats.
    # relationInfluence = 0.3 # How much relationships affect event chance, calculated as (1+influence)^(relationship level*eventInfluenceLevel)
    # Note that objects that fully disable a event should still do so!

    # Initialize Events
    events = ArenaUtils.LoadJSONIntoDictOfEventObjects(os.path.join('Contestants', 'Contestant.json'), settings)
    eventsActive = {x: True for x in events} # Global array that permits absolute disabling of events regardless of anything else. This could also be done by directly setting the base weight to 0, but this is clearer.

    # Import and initialize contestants -> going to make it dictionary name : (imageName, baseStats...)
    contestants = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Contestants', 'Contestant.json'), settings, Contestant)
    # If number of contestants in settings less than those found in the json, randomly remove some
    contestantNames = contestants.keys()
    if settings['numContestants'] < len(contestantNames):
        contestantNames = random.sample(contestantNames, len(contestantNames)-settings['numContestants'])
        for remove in contestantNames:
            del contestants[remove]
    # If number of contestants in settings more than those found in the json, add Rando Calrissians
    for i in range(len(contestantNames), settings['numContestants']):
        # Here contestants[0].stats is used as a template for making random stats
        contestants['Rando Calrissian ' + i] = Contestant.makeRandomContestant('Rando Calrissian ' + i, "DUMMY_IMAGE", contestants[0].stats, settings) # need Rando image to put here
        
    assert(len(contestants)==settings['numContestants'])

    # Import and initialize sponsors -> going to make it dictionary name : (imageName,baseStats...)
    # baseStats =  weight (probability relative to other sponsors, default 1), objectPrefs (any biases towards or away any \
    # from any type of object gift, otherwise 1, Anything else we think of)
    # No placeholder sponsors because of the way it is handled.
    sponsors = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Sponsors', 'Sponsor.json'), settings, Sponsor)

    # for now relationship levels (arbitrarily, -10 to 10, starting at zero) are stored in this dict. Later on we can make relationship objects to store, if this is somehow useful.
    friendships = {} #Storing it like this is more memory-intensive than storing pointers in the contestants, but globally faster.
    loveships = {}
    for contestant in contestants:
        friendships[contestant]={}
        loveships[contestant]={}
    for contestant1, contestant2 in itertools.combinations(contestants.keys() + sponsors.keys(), 2):
        friendships[contestant1.name][contestant2.name] = 0  # Relationships can be bidirectional. Dict keys must be immutable and tuples are only immutable if all their entries are.
        friendships[contestant2.name][contestant1.name)] = 0
        loveships[contestant1.name][contestant2.name] = 0
        loveships[contestant2.name][contestant1.name] = 0


    # Import and initialize Items -> going to make it dictionary name : (imageName,baseStats...)
    items = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Items', 'Item.json'), settings, Item)

    # Initialize World - Maybe it should have its own settings?
    # a list of one, so it's passed by refernece. Yes this is dumb.
    arena = [World(settings)] #Maybe other arguments in future, i.e. maybe in an extended world items can be found on the ground, but leaving this as-is for now.
    
    turnNumber = [0] # Deliberately a list of 1, so it's passed by reference
    state = {
    "contestants": contestants,
    "sponsors": sponsors,
    "events": events,
    "eventsActive": eventsActive,
    "items": items,
    "arena": arena,
    "friendships": friendships,
    "loveships": loveships,
    "turnNumber": turnNumber,
    } # Allows for convenient passing of the entire game state to anything that needs it (usually events)
    
    # CALLBACKS
    # This would be better done in a more object-oriented manner, but meh for now. Also, for now, relationship callbacks are in ArenaUtils
    # As much as possible influence event processing from here. Note that these callbacks happen IN ORDER
    
    # modifyBaseWeights: Expected args: baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, turnNumber. Modify in place.
        # Also a good time to do any beginning of turn stuff
    modifyBaseWeights = []    
    # modifyIndivActorWeights: Expected args: actor, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
    modifyIndivActorWeights = [
    contestantIndivActorCallback,
    partial(relationsMainWeightCallback, friendships, loveships, settings),
    ]
    # modifyIndivActorWeightsWithParticipants: Expected args: actor, participant, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
    modifyIndivActorWeightsWithParticipants = [
    contestantIndivActorWithParticipantsCallback,
    partial(relationsParticipantWeightCallback, friendships, loveships, settings),
    ]
    # modifyIndivActorWeightsWithVictims: Expected args: actor, victim, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
    modifyIndivActorWeightsWithVictims = [
    contestantIndivActorWithVictimsCallback,
    partial(relationsVictimWeightCallback, friendships, loveships, settings),
    ]
    
    callbacks = {"modifyBaseWeights": modifyBaseWeights,
                 "modifyIndivActorWeights": modifyIndivActorWeights,
                 "modifyIndivActorWeightsWithParticipants": modifyIndivActorWeightsWithParticipants,
                 "modifyIndivActorWeightsWithVictims": modifyIndivActorWeightsWithVictims,
    }
    state["callbacks"] = callbacks # I define state before callbacks so it can be bound to a callback if necessary
    
    # Run simulation

    # General pseudocode idea
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
    
    # Main loop of DEATH
    while [contestants[x].alive for x in contestants].count()>1:
        turnNumber[0] += 1
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
            actor = liveContestants[contestantKey]
            alreadyUsed.add(contestantKey)
            # Calculate individualized/multi-contestant corrected event probabilities
            indivProb = {}
            eventParticipantWeights = {} # We're about to calculate it here, and we don't want to recalculate when we get to the *next* for loop, so let's save it
            eventVictimWeights = {} # We're about to calculate it here, and we don't want to recalculate when we get to the *next* for loop, so let's save it
            for eventName, event in events.items():
                indivProb[eventName] = baseEventActorWeights[event]
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
                    validParticipants.difference_update([x.eventDisabled[eventName]["participant"] for x in validParticipants)
                    eventParticipantWeights[eventName]= {}
                    if len(validParticipants) < event.baseProps["numParticipants"]:
                        indivProb[eventName] = 0 # This event cannot happen
                        continue
                    for participant in validParticipants:
                        eventParticipantWeights[eventName][participant] = baseEventParticipantWeights[eventName]
                        eventMayProceed = True
                        for callback in callbacks["modifyIndivActorWeightsWithParticipants"]:
                            eventParticipantWeights[eventName][participant], eventMayProceed = callback(actor, liveContestants[participant],
                                                                                                        eventParticipantWeights[eventName][participant],
                                                                                                        event)
                            if not eventMayProceed:
                                break
                        if not eventMayProceed:
                            continue
                    correctionParticipantWeights = sorted(eventParticipantWeights[eventName].itervalues(),reverse=True) # The probabilities here are sketchy, but probably okay for outside appearance
                    correctionParticipantWeights = correctionParticipantWeights(:event.baseProps["numParticipants"])
                    indivProb[eventName] *= reduce(lambda x, y: x * y, correctionParticipantWeights)/(origIndivWeight**event.baseProps["numParticipants"])
                if eventName in baseEventVictimWeights:
                    # A bit of set magic
                    validVictims = set(liveContestants) - alreadyUsed
                    validVictims.difference_update([x.eventDisabled[eventName]["victim"] for x in validVictims)
                    if len(validVictims) < event.baseProps["numVictims"]:
                        indivProb[eventName] = 0 # This event cannot happen
                        continue
                    eventVictimWeights[eventName] = {}
                    for victim in validVictims:
                        eventVictimWeights[eventName][victim] = baseEventParticipantWeights[eventName]
                        eventMayProceed = True
                        for callback in callbacks["modifyIndivActorWeightsWithVictims"]:
                            eventVictimWeights[eventName][victim], eventMayProceed = callback(actor, liveContestants[victim],
                                                                                                        eventVictimWeights[eventName][victim],
                                                                                                        event)
                            if not eventMayProceed:
                                break
                        if not eventMayProceed:
                            continue   
                    correctionVictimWeights = sorted(victimWeights.itervalues(),reverse=True)
                    correctionVictimWeights = correctionVictimWeights(:event.baseProps["numVictims"])
                    correctionVictimWeights = reduce(lambda x, y: x * y, correctionVictimWeights)
                    indivProb[eventName] *= correctionVictimWeights/(origIndivWeight**event.baseProps["numVictims"])
            
            #Now select which event happens and make it happen, selecting additional participants and victims by the relative chance they have of being involved.
                

if __name__ == "__main__":
    main()
