# a file to test various theories I have as to the source of the crashing bug...

import collections
import json
import os

from Objs.Events.IndividualEventHandler import IndividualEventHandler
from Objs.Events import *
import Objs.Utilities.ArenaUtils as ArenaUtils

# Fake partial startup.

# State initialization. This should NEVER EVER be reassigned.
state = collections.OrderedDict()

# Import Settings from JSON -> going to make it a dictionary
with open('Settings.json') as settings_file:
    settings = ArenaUtils.JSONOrderedLoad(settings_file)

 # Initialize Events
# Ugly, but oh well.
Event.Event.stateStore[0] = state
events = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join(
    'Objs', 'Events', 'Events.json'), settings, Event.Event)

state["settings"] = settings
# Allows for convenient passing of the entire game state to anything that needs it (usually events)
state["events"] = events

# Arbitrary storage specifically for non-main objects/callbacks to use. Make sure to use a unique key (ideally involving the name of the function)
callbackStore = collections.OrderedDict()

state["callbackStore"] = callbackStore

# CALLBACKS
# As much as possible influence event processing from here. Note that these callbacks happen IN ORDER. It would be possible to do this in a more
# modular manner by defining a callback object, defining a registering function, using decorators... but that provides effectively no control on
# the order of operation. For now, it is better to just have it like this.

# Also, for now, relationship callbacks are in ArenaUtils

# Run once before the start of the game. Expected args: state. Modify in place.
startup = [
]

# modifyBaseWeights: Expected args: baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, baseEventSponsorWeights, turnNumber. Modify in place.
# Also a good time to do any beginning of turn stuff
modifyBaseWeights = []

# modifyIndivActorWeights: Expected args: actor, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
modifyIndivActorWeights = [
]
# modifyIndivActorWeightsWithParticipants: Expected args: actor, participant, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
modifyIndivActorWeightsWithParticipants = [
]
# modifyIndivActorWeightsWithVictims: Expected args: actor, victim, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
modifyIndivActorWeightsWithVictims = [
]

# modifyIndivActorWeightsWithSponsors: Expected args: actor, sponsor, baseEventActorWeight, event. Return newWeight, bool eventMayProceed
modifyIndivActorWeightsWithSponsors = [
]

# In case it ever becomes a good idea to directly manipulate events as they happen. Expected args: contestantKey, thisevent, state, participants, victims, sponsorsHere. Return: bool proceedAsUsual, resetEvent (True if you want the usual event chain to still happen, and True if you want the event to Reset entirely)
# Note that if *any* of these returns "unusually", then normal event processing is overridden and no further callbacks occur
overrideContestantEvent = []

# Things that happen after event processing (usually logging or emergency reset. Note that resetting callbacks need to happen before logging.
# Expected args: proceedAsUsual, eventOutputs, thisevent, contestants[contestantKey], state, participants, victims, sponsorsHere
postEventCallbacks = [
]
# Conditions for ending the game. Expected args: liveContestants, state. Return: bool endGame. (True if you want game to end)
endGameConditions = [
]

postDayCallbacks = [  # Things that happen after each day
]

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

print("Deep copying state...")
initialState = copy.deepcopy(state)

print(callbacks)


# Make dummy IndividualEventHandler
# Copy of the sick with fever event
print("Making Event Handler...")
eventHandler = IndividualEventHandler.IndividualEventHandler(state)
eventHandler.setEventWeightForSingleContestant(
    "RecoversFromFever", "Akemi Homura", 10)
eventHandler.setEventWeightForSingleContestant(
    "DiesFromFever", "Akemi Homura", 10)
eventHandler.setEventWeightForSingleContestant(
    "FriendGivesMedicine", "Akemi Homura", 10)
eventHandler.banEventForSingleContestant("SickWithFever", "Akemi Homura")
# registers event chain
state["events"]["SickWithFever"].eventStore["Akemi Homura"] = eventHandler

print(state["events"]
      ["SickWithFever"].eventStore["Akemi Homura"].callbackReferences)

print(callbacks)

print("Destroying Event Handler...")

# Destroy Event Handler
state["events"]["SickWithFever"].eventStore["Akemi Homura"] .clear()
del state["events"]["SickWithFever"].eventStore["Akemi Homura"]

print(callbacks)

# Make dummy IndividualEventHandler
# Copy of the sick with fever event
print("Making Event Handler...")
eventHandler = IndividualEventHandler.IndividualEventHandler(state)
eventHandler.setEventWeightForSingleContestant(
    "RecoversFromFever", "Akemi Homura", 10)
eventHandler.setEventWeightForSingleContestant(
    "DiesFromFever", "Akemi Homura", 10)
eventHandler.setEventWeightForSingleContestant(
    "FriendGivesMedicine", "Akemi Homura", 10)
eventHandler.banEventForSingleContestant("SickWithFever", "Akemi Homura")
# registers event chain
state["events"]["SickWithFever"].eventStore["Akemi Homura"] = eventHandler

print(state["events"]
      ["SickWithFever"].eventStore["Akemi Homura"].callbackReferences)

print(callbacks)

print("Restoring previous state...")

state.clear()
state.update(initialState.copy())
settings = state['settings']
events = state['events']
callbackStore = state['callbackStore']
thisWriter = state['thisWriter']
callbacks = state['callbacks']
Event.stateStore = state
