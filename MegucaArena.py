#!/usr/bin/env python
"""The main for the battle royale sim"""

# In case of Python 2+. The Python 3 implementation is way less dumb.
from __future__ import division

import sys
import copy
import json
import os
# Used to backup and potentially restore the random seed, for debugging purposes.
import pickle
import random  # A not very good random library, but probably fine for our purposes
import statistics  # Note: this is Python 3.4 +
import collections
from functools import partial  # Might be useful later
import traceback
import warnings

from Objs.Contestants.Contestant import Contestant, contestantIndivActorCallback, contestantIndivActorWithParticipantsCallback, contestantIndivActorWithVictimsCallback
from Objs.Items.Item import Item, ItemInstance
from Objs.Items.Status import Status
from Objs.Sponsors.Sponsor import Sponsor, contestantIndivActorWithSponsorsCallback
from Objs.World.World import World
from Objs.Relationships.Relationship import Relationship
import Objs.Utilities.ArenaUtils as ArenaUtils
from Objs.Events import *
# If we get more stuff here, we're going to have to do something better
from Objs.Items import DiseaseItems
from Objs.Display.HTMLWriter import HTMLWriter

PRINTHTML = True
DEBUG = True
STATSDEBUG = collections.OrderedDict()
CONFIG_FILE_PATHS = {"settings": "Settings.json",
                     "phases": "Phases.json",
                     "events": os.path.join('Objs', 'Events', 'Events.json'),
                     "contestants": os.path.join('Objs', 'Contestants', 'Contestants.json'),
                     "sponsors": os.path.join('Objs', 'Sponsors', 'Sponsors.json')}

# Object used by the MegucaArena Main to store and track probability details about the events under consideration for a given contestant.
class EventSelectionState:

    # Static look-up tables, hard-coded participants/victims/sponsorsHere
    callbackNames = ArenaUtils.DictToOrderedDict({
        "participant": "modifyIndivActorWeightsWithParticipants",
        "victim": "modifyIndivActorWeightsWithVictims",
        "sponsor": "modifyIndivActorWeightsWithSponsors"
    })
    
    peopleList = ArenaUtils.DictToOrderedDict({
        "participant": "contestants",
        "victim": "contestants",
        "sponsor": "sponsors"
    })
    
    basePropNumField = ArenaUtils.DictToOrderedDict({
        "participant": "numParticipants",
        "victim": "numVictims",
        "sponsor": "numSponsors"
    })

    def __init__(self, actor, baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, baseEventSponsorWeights, state, liveContestants, alreadyUsed):
        self.actor = actor
        # individualized/multi-contestant corrected event probabilities
        self.indivProb = copy.deepcopy(baseEventActorWeights)
        # Copies of the general event weights; Should not be modified by this class
        self.baseEventWeights = collections.OrderedDict()
        self.baseEventWeights["actor"] = baseEventActorWeights
        self.baseEventWeights["participant"] = baseEventParticipantWeights
        self.baseEventWeights["victim"] = baseEventVictimWeights
        self.baseEventWeights["sponsor"] = baseEventSponsorWeights
        # Personalized Weights for this contestant as main actor.
        self.eventWeights = collections.OrderedDict()
        self.eventWeights["participant"] = ArenaUtils.DefaultOrderedDict(
            collections.OrderedDict)
        self.eventWeights["victim"] = ArenaUtils.DefaultOrderedDict(
            collections.OrderedDict)
        self.eventWeights["sponsor"] = ArenaUtils.DefaultOrderedDict(
            collections.OrderedDict)
        # Number of participants rolled for each event.
        self.trueNumRoles = collections.OrderedDict()
        self.trueNumRoles["participant"] = ArenaUtils.DefaultOrderedDict(int)
        self.trueNumRoles["victim"] = ArenaUtils.DefaultOrderedDict(int)
        self.trueNumRoles["sponsor"] = ArenaUtils.DefaultOrderedDict(int)
        # State reference to the global state.
        self.state = state
        self.liveContestants = liveContestants
        self.alreadyUsed = alreadyUsed
    
    # Predetermine number of participants/victims. Returns False if impossible.
    def selectNumberRoles(self, event):
        eventName = str(event)
        numExtraAllowed = len(self.liveContestants) - (event.baseProps["numParticipants"] if "numParticipants" in event.baseProps else 0) - (
            event.baseProps["numVictims"] if "numVictims" in event.baseProps else 0) - 1
        if numExtraAllowed < 0:
            self.indivProb[eventName] = 0
            return False

        # Set initial values based on eventName in base props (do sponsors as well here)
        for roleName in self.callbackNames:
            if self.basePropNumField[roleName] in event.baseProps:
                self.trueNumRoles[roleName][eventName] = event.baseProps[self.basePropNumField[roleName]]

        if "numVictimsExtra" in event.baseProps and "numParticipantsExtra" in event.baseProps:
            numExtraParticipants = round(event.baseProps["numParticipantsExtra"] / (
                event.baseProps["numParticipantsExtra"] + event.baseProps["numVictimsExtra"])) * numExtraAllowed            
            numExtraVictims = numExtraAllowed - numExtraParticipants
            self.trueNumRoles["participant"][eventName] += random.randint(
                0, min(event.baseProps["numParticipantsExtra"], numExtraParticipants))
            self.trueNumRoles["victim"][eventName] += random.randint(
                0, min(event.baseProps["numVictimsExtra"], numExtraVictims))
        elif "numVictimsExtra" in event.baseProps:
            self.trueNumRoles["victim"][eventName] += random.randint(
                0, min(event.baseProps["numVictimsExtra"], numExtraAllowed))
        elif "numParticipantsExtra" in event.baseProps:
            self.trueNumRoles["participant"][eventName] += random.randint(
                0, min(event.baseProps["numParticipantsExtra"], numExtraAllowed))
        return True
    
    # Adjusts Event Probabilities for the presence of multiple actors.
    def modifyWeightForMultipleActors(self, event, origIndivWeight):
        for roleName in self.callbackNames:
            weights = self.eventWeights[roleName]
            trueNumRoles = self.trueNumRoles[roleName]
            baseWeights = self.baseEventWeights[roleName]
            eventName = str(event)
            callbackName = self.callbackNames[roleName]
            people = self.state[self.peopleList[roleName]]
            if eventName in baseWeights:
                if not trueNumRoles[eventName]:
                    return
                if not origIndivWeight:  # this causes numerical issues and should end up 0 anyway
                    self.indivProb[eventName] = 0.0
                    return
                # A bit of set magic
                if roleName == "sponsor":
                    validRoles = people.keys()
                elif roleName in ["participant", "victim"]:
                    validRoles = set(self.liveContestants) - self.alreadyUsed
                    for x in validRoles:
                        try:
                            validRoles.difference_update(
                                people[x].eventDisabled[eventName][roleName])
                        except:
                            pass
                    if len(validRoles) < trueNumRoles[eventName]:
                        self.indivProb[eventName] = 0  # This event cannot happen
                        return
                else:
                    raise Exception("Invalid Role!")
                validRoles = sorted(list(validRoles))
                for role in validRoles:
                    weights[eventName][role] = baseWeights[eventName]
                    eventMayProceed = True
                    for callback in self.state["callbacks"][callbackName]:
                        weights[eventName][role], eventMayProceed = callback(self.actor, people[role],
                                                                             weights[eventName][role],
                                                                             event)
                        if not eventMayProceed:
                            break
                if sum(bool(x) for x in weights[eventName].values()) < trueNumRoles[eventName]:
                    self.indivProb[eventName] = 0
                    return
                correctionRoleWeight = sum(
                    weights[eventName].values()) / len(weights)
                self.indivProb[eventName] *= max(min(correctionRoleWeight /
                                                 origIndivWeight, self.state["settings"]["maxParticipantEffect"]), 1/self.state["settings"]["minParticipantEffect"])
        # the above precalculation fails if some victims or participants are invalid, so an additional check is necessary; Unfortunately this distorts the statistics a little.
        if self.eventWeights["victim"][eventName] and self.eventWeights["participant"][eventName]:
            if self.trueNumRoles["participant"][eventName] + self.trueNumRoles["victim"][eventName] + list(self.eventWeights["victim"][eventName].values()).count(0) + list(self.eventWeights["participant"][eventName].values()).count(0) > len(set(list(self.eventWeights["victim"][eventName]) + list(self.eventWeights["participant"][eventName]))):
                self.indivProb[eventName] = 0
                
    # Selects contestants to play each role in an event based on their weights.
    def selectRoles(self, eventName, roleName, weights=None):
        if weights is None:
            weights = self.eventWeights[roleName]
        trueNumRoles = self.trueNumRoles[roleName]
        baseWeights = self.baseEventWeights[roleName]
        people = self.state[self.peopleList[roleName]]
        if eventName in baseWeights and trueNumRoles[eventName] > 0:
            rolekeys = ArenaUtils.weightedDictRandom(
                weights[eventName], trueNumRoles[eventName])
            roles = [people[key] for key in rolekeys]
        else:
            roles = []
        return roles
    
                     

class MegucaArena:
    # Hmm...make object feeding list or dict based?
    def __init__(self, configFilePaths, eventClass=Event.Event, contestantClass=Contestant, sponsorClass=Sponsor, relationshipClass=Relationship):
        # Initial Setup:
        self.state = collections.OrderedDict()
        self.configFilePaths = configFilePaths
        self.loadParametersFromJSON()
         # TODO: Now that the item stats etc. are relatively set, should have the object loaders inspect the final dictionaries for correctness (no misspellings etc.) (since json doesn't have a mechanism for checking)
        self.initializeEvents(eventClass)
        self.initializeContestants(contestantClass)
        # Import and initialize sponsors -> going to make it dictionary name : (imageName,baseStats...)
        # baseStats =  weight (probability relative to other sponsors, default 1), objectPrefs (any biases towards or away any \
        # from any type of object gift, otherwise 1, Anything else we think of)
        # No placeholder sponsors because of the way it is handled.
        self.sponsors = ArenaUtils.LoadJSONIntoDictOfObjects(self.configFilePaths["sponsors"], self.settings, sponsorClass)
        self.allRelationships = relationshipClass(self.contestants, self.sponsors, self.settings)
        
    def loadParametersFromJSON(self):
        # Import Settings from JSON -> going to make it a dictionarys
        with open(self.configFilePaths["settings"]) as settings_file:
            self.settings = ArenaUtils.JSONOrderedLoad(settings_file)
        with open(self.configFilePaths["phases"]) as phases_file:
            self.phases = ArenaUtils.JSONOrderedLoad(phases_file)
       
    def initializeEvents(self, eventClass):
        eventClass.stateStore[0] = self.state
        self.events = ArenaUtils.LoadJSONIntoDictOfObjects(self.configFilePaths["events"], self.settings, eventClass)
        # This dict allows for absolute disabling of events by setting False.
        self.eventsActive = ArenaUtils.DictToOrderedDict({x: True for x in self.events})

    def initializeContestants(self, contestantClass):
        contestantClass.stateStore[0] = self.state
        # Import and initialize contestants -> going to make it dictionary name : (imageName, baseStats...)
        self.contestants = ArenaUtils.LoadJSONIntoDictOfObjects(self.configFilePaths["contestants"], self.settings, contestantClass)
        # Initialize stats
        # Deduce stats from the union of all contestants - if there are any typos this is a problem.
        statTemplate = set()
        for x in self.contestants.values():
            statTemplate |= set(list(x.stats.keys()))
        # This is kind of dumb, but easiest: If we want pure random stats, any stats in the file are directly overwritten.
        if self.settings['fullRandomStats']:
            for key, value in self.contestants.items():
                self.contestants[key] = Contestant.makeRandomContestant(
                    value.name, value.gender, value.imageFile, statTemplate, self.settings)
        else:  # fill in missing stats for any contestants
            for value in self.contestants.values():
                value.contestantStatFill(statTemplate)
        # Adjust contestant count to the desired value
        if not self.settings['matchContestantCount']:
            # If number of contestants in settings less than those found in the json, randomly remove some
            contestantNames = self.contestants.keys()
            if self.settings['numContestants'] < len(contestantNames):
                contestantNames = random.sample(contestantNames, len(
                    contestantNames) - self.settings['numContestants'])
                for remove in contestantNames:
                    del self.contestants[remove]
            # If number of contestants in settings more than those found in the json, add Rando Calrissians
            for i in range(len(contestantNames), self.settings['numContestants']):
                # Here contestants[0].stats is used as a template for making random stats
                self.contestants['Rando Calrissian ' + str(i)] = Contestant.makeRandomContestant(
                    'Rando Calrissian ' + str(i), "M", "Rando.jpg", statTemplate, self.settings)  # need Rando image to put here

            assert(len(self.contestants) == self.settings['numContestants'])
        else:
            self.settings['numContestants'] = len(self.contestants)
        # Normalize stats if necessary
        if self.settings["statNormalization"]:
            targetSum = sum(sum(x.stats.values())
                            for x in self.contestants.values()) / len(self.contestants)
        for contestant in self.contestants.values():
            if self.settings["statNormalization"]:
                contestant.contestantStatNormalizer(targetSum)
            contestant.InitializeEventModifiers(self.events)        
        
    def main(self):
        """The main for the battle royale sim"""

        # List of settings as I come up with them. It can stay as a dict. THIS IS OUT OF DATE.
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

        # Import and initialize Items -> going to make it dictionary name : (imageName,baseStats...)
        items = ArenaUtils.LoadJSONIntoDictOfObjects(
            os.path.join('Objs', 'Items', 'Items.json'), self.settings, Item)
        ItemInstance.stateStore[0] = self.state
        statuses = ArenaUtils.LoadJSONIntoDictOfObjects(
            os.path.join('Objs', 'Items', 'Statuses.json'), self.settings, Status)

        # Initialize World - Maybe it should have its own settings?
        # Maybe other arguments in future, i.e. maybe in an extended world items can be found on the ground, but leaving this as-is for now.
        arena = World(self.settings)

        turnNumber = [0]  # Deliberately a list of 1, so it's passed by reference

        # Arbitrary storage specifically for non-main objects/callbacks to use. Make sure to use a unique key (ideally involving the name of the function)
        callbackStore = collections.OrderedDict()

        thisWriter = None  # current HTML display object

        self.state.update(ArenaUtils.DictToOrderedDict({
            "settings": self.settings,
            "contestants": self.contestants,
            "sponsors": self.sponsors,
            "events": self.events,
            "eventsActive": self.eventsActive,
            "items": items,
            "statuses": statuses,
            "arena": arena,
            "allRelationships": self.allRelationships,
            "turnNumber": turnNumber,
            "callbackStore": callbackStore,
            "thisWriter": thisWriter,
            "phases": self.phases
        }))  # Allows for convenient passing of the entire game state to anything that needs it (usually events)
        # An unfortunate bit of split processing
        for sponsor in self.sponsors.values():
            sponsor.initializeTraits(self.state)
        # CALLBACKS
        # As much as possible influence event processing from here. Note that these callbacks happen IN ORDER. It would be possible to do this in a more
        # modular manner by defining a callback object, defining a registering function, using decorators... but that provides effectively no control on
        # the order of operation. For now, it is better to just have it like this.

        # Also, for now, relationship callbacks are in ArenaUtils

        # Run once before the start of the game. Expected args: state. Modify in place.
        startup = [
            ArenaUtils.loggingStartup,
            ArenaUtils.sponsorTraitWrite]
        # Example debug rig to give an item to everyone: add the functor partial(ArenaUtils.giveEveryoneItem, "Dossier")
        # to this list.

        if PRINTHTML:
            startup.insert(0, ArenaUtils.relationshipWrite)

        # modifyBaseWeights: Expected args: liveContestants, baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, baseEventSponsorWeights, turnNumber, state. Modify in place.
            # Also a good time to do any beginning of turn stuff
        modifyBaseWeights = [
            ArenaUtils.logContestants,
            ArenaUtils.resetKillFlag]

        # modifyIndivActorWeights: Expected args: actor, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
        modifyIndivActorWeights = [
            partial(ArenaUtils.eventMayNotRepeat, state=self.state),
            contestantIndivActorCallback,
            self.allRelationships.relationsMainWeightCallback
        ]
        # modifyIndivActorWeightsWithParticipants: Expected args: actor, participant, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
        modifyIndivActorWeightsWithParticipants = [
            contestantIndivActorWithParticipantsCallback,
            partial(self.allRelationships.relationsRoleWeightCallback, "Participant")
        ]
        # modifyIndivActorWeightsWithVictims: Expected args: actor, victim, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
        modifyIndivActorWeightsWithVictims = [
            contestantIndivActorWithVictimsCallback,
            partial(self.allRelationships.relationsRoleWeightCallback, "Victim")
        ]

        modifyIndivActorWeightsWithParticipantsAndVictims = [
        ]

        # modifyIndivActorWeightsWithSponsors: Expected args: actor, sponsor, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
        modifyIndivActorWeightsWithSponsors = [
            contestantIndivActorWithSponsorsCallback,
            partial(self.allRelationships.relationsRoleWeightCallback, "Sponsor")
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

        postEventWriterCallbacks = [  # For piggy-backing after events if you need to write to the main HTML. Args: thisWriter, eventOutputs, thisEvent, state. Returns: None.
            ArenaUtils.relationshipUpdate
        ]

        # Conditions for ending the game. Expected args: liveContestants, state. Return: bool endGame. (True if you want game to end)
        endGameConditions = [
            ArenaUtils.onlyOneLeft
        ]

        preDayCallbacks = [  # Things that happen before each day. Args: state. Returns: None.
        ]

        postDayCallbacks = [  # Things that happen after each day. Args: state. Returns: None.
            self.allRelationships.decay
        ]

        if PRINTHTML:
            postDayCallbacks.insert(0, ArenaUtils.injuryAndStatusWrite)
            postDayCallbacks.insert(0, ArenaUtils.killWrite)
            postDayCallbacks.insert(0, ArenaUtils.relationshipWrite)

        postGameCallbacks = [
        ]

        if PRINTHTML:
            postGameCallbacks.insert(0, ArenaUtils.killWrite)
            postGameCallbacks.insert(0, ArenaUtils.relationshipWrite)

        self.callbacks = ArenaUtils.DictToOrderedDict({"startup": startup,
                                                       "modifyBaseWeights": modifyBaseWeights,
                                                       "modifyIndivActorWeights": modifyIndivActorWeights,
                                                       "modifyIndivActorWeightsWithParticipants": modifyIndivActorWeightsWithParticipants,
                                                       "modifyIndivActorWeightsWithPartipantsAndVictims": modifyIndivActorWeightsWithParticipantsAndVictims,
                                                       "modifyIndivActorWeightsWithVictims": modifyIndivActorWeightsWithVictims,
                                                       "modifyIndivActorWeightsWithSponsors": modifyIndivActorWeightsWithSponsors,
                                                       "overrideContestantEvent": overrideContestantEvent,
                                                       "postEventCallbacks": postEventCallbacks,
                                                       "postEventWriterCallbacks": postEventWriterCallbacks,
                                                       "endGameConditions": endGameConditions,
                                                       "preDayCallbacks": preDayCallbacks,
                                                       "postDayCallbacks": postDayCallbacks,
                                                       "postGameCallbacks": postGameCallbacks,
                                                       })

        # loophole that allows event-defining and item/status-defining files to slip callbacks in
        for store, funcList in list(Event.Event.inserted_callbacks.items()) + list(Item.inserted_callbacks.items()):
            self.callbacks[store].extend(funcList)

        self.state["callbacks"] = self.callbacks

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

        # Startup callbacks
        for callback in self.callbacks["startup"]:
            callback(self.state)

        # Main loop of DEATH
        STATSDEBUG["allEvents"] = ArenaUtils.DefaultOrderedDict(
            int) if "allEvents" not in STATSDEBUG else STATSDEBUG["allEvents"]
        while True:
            turnNumber[0] += 1
            if turnNumber[0] in self.phases:
                thisDay = self.phases[turnNumber[0]]
            else:
                thisDay = self.phases["default"]
            print("Day " + str(turnNumber[0]))
            for callback in self.callbacks["preDayCallbacks"]:
                callback(self.state)
            for phaseNum, thisPhase in enumerate(thisDay["phases"]):
                titleString = thisDay["titles"][phaseNum]
                self.state["curPhase"] = thisPhase
                self.eventsActive = ArenaUtils.DictToOrderedDict({eventName: True for eventName, x in self.events.items(
                ) if "phase" not in x.baseProps or thisPhase in x.baseProps["phase"]})
                while True:  # this just allows resetting the iteration
                    if PRINTHTML:
                        thisWriter = HTMLWriter(statuses)
                        thisWriter.addTitle(
                            titleString.replace('#', str(turnNumber[0])))
                    # If set to true, this runs end of turn processing. Otherwise it reloops immediately. Only used if turn is reset.
                    restartTurn = False
                    # Obviously very klunky and memory-intensive, but only clean way to allow resets under the current paradigm. The other option is to force the last event in a turn to never kill the last contestant.
                    initialState = copy.deepcopy(self.state)
                    liveContestants = ArenaUtils.DictToOrderedDict(
                        {x: y for x, y in self.contestants.items() if y.alive})
                    if phaseNum == 0:  # I want to be explicit here
                        origLiveContestants = copy.copy(liveContestants)
                    # Sample contestants randomly
                    randOrderContestantKeys = random.sample(
                        liveContestants.keys(), len(liveContestants))
                    # Get base event weights (now is the time to shove in the effects of any special turn, whenever that gets implemented)
                    baseEventActorWeights = ArenaUtils.DictToOrderedDict(
                        {x: y.baseProps["mainWeight"] if x in self.eventsActive and self.eventsActive[x] else 0 for x, y in self.events.items()})
                    baseEventParticipantWeights = ArenaUtils.DictToOrderedDict(
                        {x: y.baseProps["participantWeight"] for x, y in self.events.items() if "participantWeight" in y.baseProps})
                    baseEventVictimWeights = ArenaUtils.DictToOrderedDict(
                        {x: y.baseProps["victimWeight"] for x, y in self.events.items() if "victimWeight" in y.baseProps})
                    baseEventSponsorWeights = ArenaUtils.DictToOrderedDict(
                        {x: y.baseProps["sponsorWeight"] for x, y in self.events.items() if "sponsorWeight" in y.baseProps})
                    # Do callbacks for modifying base weights
                    for callback in self.callbacks["modifyBaseWeights"]:
                        callback(liveContestants, baseEventActorWeights, baseEventParticipantWeights,
                                 baseEventVictimWeights, baseEventSponsorWeights, turnNumber, self.state)
                    # Now go through the contestants and trigger events based on their individualized probabilities
                    alreadyUsed = set()
                    # This is not statistically uniform because these multi-person events are hard and probably not worth figuring out in exact detail...
                    for contestantKey in randOrderContestantKeys:
                        if contestantKey in alreadyUsed:
                            continue
                        # Some contestants may die in events, they get removed at the end of the for loop
                        actor = liveContestants[contestantKey]
                        alreadyUsed.add(contestantKey)                        
                        itcounter = 0
                        selectionState = EventSelectionState(
                            actor, baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, baseEventSponsorWeights, self.state, liveContestants, alreadyUsed)
                        while True:
                            for eventName, event in self.events.items():
                                eventMayProceed = True
                                for callback in self.callbacks["modifyIndivActorWeights"]:
                                    selectionState.indivProb[eventName], eventMayProceed = callback(
                                        actor, selectionState.indivProb[eventName], event)
                                    if not eventMayProceed:  # If one returns false, it signals that the event has been blocked
                                        break
                                if not eventMayProceed:
                                    continue
                                origIndivWeight = selectionState.indivProb[eventName]
                                if not selectionState.selectNumberRoles(event):
                                    continue
                                selectionState.modifyWeightForMultipleActors(event, origIndivWeight)
                                
                            # If ALL events are banned, rerun this until a working combination appears
                            if sum(selectionState.indivProb.values()):
                                break
                            # There's a few edge cases where it's really hard to keep infinite loop from happening, so if that happens, just give up
                            if itcounter > 4:
                                selectionState.indivProb = copy.deepcopy(baseEventActorWeights)
                                warnings.warn("Reached cycle limit on trying to find valid event probabilities; reverting to fallback.")
                                break
                            itcounter += 1
                        # It is occasionally useful for an event to be able to force a new event to be chosen.
                        # While computationally wasteful, this prevents us from needing to make a special callback for
                        # events with unique trigger conditions. Events may signal for a reselection by returning None or []
                        # Note, however, that this _not_ a good way to enforce specific participants, etc. as this is both wasteful
                        # and not-statistically accurate.
                        # Ugly Hack, but not sure there's a better way. We need pre-event information on contestants, and short of deepcopying everything...
                        preEventInjuries = ArenaUtils.DictToOrderedDict(
                            {x: self.contestants[x].hasThing("Injury") for x in liveContestants})
                        self.allRelationships.backup()
                        while(True):
                            # Now select which event happens and make it happen, selecting additional participants and victims by the relative chance they have of being involved.
                            eventName = ArenaUtils.weightedDictRandom(selectionState.indivProb)[0]
                            # Handle event overrides, if any
                            # Determine participants, victims, if any.
                            thisevent = self.events[eventName]
                            victims = selectionState.selectRoles(eventName, "victim")
                            # Can't be both a participant and a victim... (this creates a bit of bias, but oh well)
                            possibleParticipantEventWeights = copy.deepcopy(
                                selectionState.eventWeights["participant"])
                            for x in victims:
                                possibleParticipantEventWeights[eventName][x.name] = 0
                            # some participants need adjustment based on the chosen victim(s)
                            aborted = self.allRelationships.reprocessParticipantWeightsForVictims(
                                possibleParticipantEventWeights, victims, self.events[eventName])
                            # check if enough possible participants are left to satisfy the event, presuming it has participants
                            if "numParticipants" in thisevent.baseProps:
                                # print(possibleParticipantEventWeights[eventName])
                                # print(len(possibleParticipantEventWeights[eventName]))
                                # print(list(possibleParticipantEventWeights[eventName].values()).count(0))
                                if len(possibleParticipantEventWeights[eventName]) - list(possibleParticipantEventWeights[eventName].values()).count(0) < selectionState.trueNumRoles["participant"][eventName]:
                                    # abort event
                                    continue
                            if DEBUG:
                                STATSDEBUG["state"] = self.state
                                STATSDEBUG["indivProb"] = selectionState.indivProb
                                STATSDEBUG["eventParticipantWeights"] = selectionState.eventWeights["participant"][eventName]
                                STATSDEBUG["participants"] = (
                                    baseEventParticipantWeights, possibleParticipantEventWeights, selectionState.trueNumRoles["participant"])
                                STATSDEBUG["mainActor"] = contestantKey
                                STATSDEBUG["eventName"] = eventName
                            # print(possibleParticipantEventWeights[eventName])
                            participants = selectionState.selectRoles(eventName, "participant", possibleParticipantEventWeights)
                            sponsorsHere = selectionState.selectRoles(eventName, "sponsor")
                            proceedAsUsual = True
                            resetEvent = False
                            for override in self.callbacks["overrideContestantEvent"]:
                                # Be very careful of modifying state here.
                                proceedAsUsual, resetEvent = override(
                                    contestantKey, thisevent, self.state, participants, victims, sponsorsHere)
                                if not proceedAsUsual or resetEvent:
                                    break
                            if resetEvent:
                                continue
                            if proceedAsUsual:
                                eventOutputs = thisevent.doEvent(
                                    self.contestants[contestantKey], self.state, participants, victims, sponsorsHere)
                                if not eventOutputs:
                                    # Apparently this event is not valid for this contestant (participants etc. should not be considered)
                                    selectionState.indivProb[eventName] = 0
                                    continue
                                eventOutputs = list(eventOutputs)
                                self.allRelationships.processTraitEffect(
                                    thisevent, self.contestants[contestantKey], participants + victims)
                            for postEvent in self.callbacks["postEventCallbacks"]:
                                postEvent(proceedAsUsual, eventOutputs, thisevent,
                                          self.contestants[contestantKey], self.state, participants, victims, sponsorsHere)
                            desc, descContestants, theDead = eventOutputs[:3]
                            break

                        print(eventName)
                        STATSDEBUG["allEvents"][eventName] += 1
                        if PRINTHTML:
                            thisWriter.addEvent(
                                desc, descContestants, self.state, preEventInjuries)
                            for callback in self.callbacks["postEventWriterCallbacks"]:
                                callback(thisWriter, eventOutputs, thisevent, self.state)
                        else:
                            print(desc)

                        # Check if everyone is now dead...
                        if all(not x.alive for x in liveContestants.values()):
                            # This turn needs to be rerun
                            self.state.clear()
                            self.state.update(initialState.copy())
                            self.settings = self.state['settings']
                            self.contestants = self.state['contestants']
                            self.callbacks = self.state['callbacks']
                            self.sponsors = self.state['sponsors']
                            self.events = self.state['events']
                            self.eventsActive = self.state['eventsActive']
                            items = self.state['items']
                            statuses = self.state['statuses']
                            arena = self.state['arena']
                            self.allRelationships = self.state['allRelationships']
                            turnNumber = self.state['turnNumber']
                            callbackStore = self.state['callbackStore']
                            thisWriter = self.state['thisWriter']
                            Event.Event.stateStore[0] = self.state
                            ItemInstance.ItemInstance.stateStore[0] = self.state
                            restartTurn = True
                            break

                        # Remove the dead contestants from the live list. Add the contestants involved to alreadyUsed.
                        for dead in theDead:
                            del liveContestants[dead]
                        if len(eventOutputs) > 4 and eventOutputs[4]:
                            alreadyUsed.update([x.name for x in eventOutputs[4]])
                        else:
                            alreadyUsed.update([x.name for x in descContestants])

                    if not restartTurn:
                        # conditions for ending the game
                        for callback in self.callbacks["endGameConditions"]:
                            if callback(liveContestants, self.state):
                                if PRINTHTML:
                                    thisWriter.addBigLine(list(liveContestants.values())[
                                                          0].name + " survive(s) the game and win(s)!")
                                    thisWriter.finalWrite(os.path.join("Assets", str(
                                        turnNumber[0]) + " Phase " + thisPhase + ".html"), self.state)
                                else:
                                    print(list(liveContestants.values())[
                                          0].name + " survive(s) the game and win(s)!")

                                for callback in self.callbacks["postGameCallbacks"]:
                                    callback(self.state)
                                return list(liveContestants.values())[0].name, turnNumber[0]
                        if PRINTHTML:
                            if phaseNum == len(thisDay["phases"]) - 1:
                                deadThisTurn = set(
                                    origLiveContestants.values()) - set(liveContestants.values())
                                if deadThisTurn:
                                    thisWriter.addEvent(
                                        "The following names were added to the memorial wall: " + Event.Event.englishList(deadThisTurn), deadThisTurn)
                            thisWriter.finalWrite(os.path.join("Assets", str(
                                turnNumber[0]) + " Phase " + thisPhase + ".html"), self.state)
                        break
            for callback in self.callbacks["postDayCallbacks"]:
                callback(self.state)
            if turnNumber[0] > 200:
                raise TooManyDays('Way too many days')


class TooManyDays(Exception):
    pass

def postmortem():
    if not DEBUG:
        return
    import pdb
    type, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)

def statCollection():  # expand to count number of days, and fun stuff like epiphany targets?
    statDict = ArenaUtils.DefaultOrderedDict(int)
    numErrors = 0
    days = []
    global PRINTHTML
    PRINTHTML = False
    for _ in range(0, 100):
        try:
            winner, day = MegucaArena(CONFIG_FILE_PATHS).main()
            statDict[winner] += 1
            days.append(day)
        except TooManyDays:
            pass
        except Exception:
            postmortem()
            numErrors += 1

    print(statDict)
    print(sum(days) / len(days))
    print(statistics.stdev(days))
    print(numErrors)
    totEvents = sum(y for y in STATSDEBUG["allEvents"].values())
    print({x: round(y / totEvents, 3)
           for x, y in STATSDEBUG["allEvents"].items()})

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--stats':
        statCollection()
    else:
        # this is deliberately mutually exclusive with "--stats"
        if len(sys.argv) > 1 and sys.argv[1] == '--loadseed':
            with open("RSEED_BACKUP", "rb") as f:
                lograndstate = pickle.load(f)
            random.setstate(lograndstate)
        else:
            lograndstate = random.getstate()
            with open("RSEED_BACKUP", "wb") as f:
                pickle.dump(lograndstate, f)
        try:
            MegucaArena(CONFIG_FILE_PATHS).main()
        except Exception as e:
            postmortem()
            raise e

