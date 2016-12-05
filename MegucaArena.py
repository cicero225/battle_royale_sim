"""The main for the battle royale sim"""

import json
import os
import random # A not very good random library, but probably fine for our purposes
import itertools # Kind of lame

from __future__ import division # In case of Python 2+. The Python 3 implementation is way less dumb.

from Contestants.Contestant import Contestant
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
    # statInfluence = 0.3 # How much stats influence event weightings, calculated as (1+influence)^(stat-5)
    # objectInfluence = 1 # How much objects in inventory affect events. The default 1 uses the base stats.
    # Note that objects that fully disable a event should still do so!


    # Initialize Arena State

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
    for contestant1, contestant2 in itertools.combinations(contestants + sponsors, 2):
        friendships[(contestant1.name, contestant2.name)] = 0 #Relationships can be bidirectional. Dict keys must be immutable and tuples are only immutable if all their entries are.
        friendships[(contestant2.name, contestant1.name)] = 0
        loveships[(contestant1.name, contestant2.name)] = 0
        loveships[(contestant2.name, contestant1.name)] = 0


    # Import and initialize Items -> going to make it dictionary name : (imageName,baseStats...)
    items = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Items', 'Item.json'), settings, Item)

    #Initialize World - Maybe it should have its own settings?
    arena = World(settings) #Maybe other arguments in future, i.e. maybe in an extended world items can be found on the ground, but leaving this as-is for now.

    # Run simulation
    # If we're going to have a cornucopia, we should remember to set up some way to have a special turn: maybe as a separate object?
    # In any case a special turn would have unique base event weights.

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
    
    state = {
    "contestants": contestants,
    "sponsors": sponsors,
    "events": events,
    "eventsActive": eventsActive,
    "items": items,
    "arena": arena,
    "friendships": friendships,
    "loveships": loveships,
    } # Allows for convenient passing of the entire game state to anything that needs it (usually events)
    
    # Main loop of DEATH - I'm going to list comprehension the hell out of this because it actually makes it clearer (I think) and a little speed is nice
    while [contestants[x].alive for x in contestants].count()>1:
        liveContestants = {x: y for x, y in contestants.items() if y.alive}
        # Sample contestants randomly
        randOrderContestantKeys = random.sample(liveContestants.keys(), len(liveContestants))
        # Get base event weights (now is the time to shove in the effects of any special turn, whenever that gets implemented)
        baseEventActorWeights = {x: y.baseProps["mainWeight"] if eventsActive[x] else 0 for x, y in events.items()} # Oh my god dictionary comprehensions exist, I have discovered a new world
        baseEventParticipantWeights = {x: y.baseProps["participantWeight"] for x, y in events.items() if "participantWeight" in y.baseProps}
        baseEventVictimWeights = {x: y.baseProps["victimWeight"] for x, y in events.items() if "victimWeight" in y.baseProps}
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
                if actor.eventDisabled[eventName]["main"]:
                    indivProb[eventName] = 0
                    continue
                # Base single event probability
                origSingleWeight = baseEventActorWeights[event]*actor.fullEventMultipliers[eventName]["main"]+actor.eventAdditions[eventName]["main"]
                indivProb[eventName] = origSingleWeight
                # Probability correction for multi-contestant events, if necessary
                if eventName in baseEventParticipantWeights:
                    # A bit of set magic
                    validParticipants = set(liveContestants) - alreadyUsed
                    validParticipants.difference_update([x.eventDisabled[eventName]["participant"] for x in validParticipants)
                    if len(validParticipants) < event.baseProps["numParticipants"]:
                        indivProb[eventName] = 0 # This event cannot happen
                        continue
                    eventParticipantWeights[eventName]= {}
                    for participant in validParticipants:
                        eventParticipantWeights[eventName][participant] = (baseEventParticipantWeights[eventName]*liveContestants[participant].fullEventMultipliers[eventName]["participant"]
                                                                           +liveContestants[participant].eventAdditions[eventName]["participant"])
                    # Sorting theory, yay. Anyway, here the number of elements we are searching for ranges wildly from close to the size of the whole list to only a small part,
                    # making heapsort based lookups anything from much slower to much faster than a full sort.
                    # Because of the way Python is, the built-ins are often substantially faster than trying to code something like quickselect by hand
                    # Python's docs even say that for large lists (>1000, though not relevant here), you should just use sorted.
                    # Thus, the best choices are probably just sorted (sort everything, even if that's obviously wasting effort) or the heapq library.
                    # Since the latter requires adding a library specifically to do this, let's just feel dumb and use sorted.
                    correctionParticipantWeights = sorted(eventParticipantWeights[eventName].itervalues(),reverse=True) # The probabilities here are sketchy, but probably okay for outside appearance
                    correctionParticipantWeights = correctionParticipantWeights(:event.baseProps["numParticipants"])
                    indivProb[eventName] *= reduce(lambda x, y: x * y, correctionParticipantWeights)/(origSingleWeight**len(:event.baseProps["numParticipants"]))
                if eventName in baseEventVictimWeights:
                    # A bit of set magic
                    validVictims = set(liveContestants) - alreadyUsed
                    validVictims.difference_update([x.eventDisabled[eventName]["victim"] for x in validVictims)
                    if len(validVictims) < event.baseProps["numVictims"]:
                        indivProb[eventName] = 0 # This event cannot happen
                        continue
                    eventVictimWeights[eventName] = {}
                    for victim in validVictims:
                        eventVictimWeights[eventName][victim] = (baseEventVictimWeights[eventName]*liveContestants[victim].fullEventMultipliers[eventName]["victim"]
                                                                +liveContestants[victim].eventAdditions[eventName]["victim"] )   
                    correctionVictimWeights = sorted(victimWeights.itervalues(),reverse=True)
                    correctionVictimWeights = correctionVictimWeights(:event.baseProps["numVictims"])
                    correctionVictimWeights = reduce(lambda x, y: x * y, correctionVictimWeights)
                    indivProb[eventName] *= correctionVictimWeights/(origSingleWeight**len(:event.baseProps["numVictims"]))
            
            #Now select which event happens and make it happen, selecting additional participants and victims by the relative chance they have of being involved.
                

if __name__ == "__main__":
    main()
