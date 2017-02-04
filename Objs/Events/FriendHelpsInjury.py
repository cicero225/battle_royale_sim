from Objs.Events.Event import Event
from collections import defaultdict
import random

def checkActorInjured(actor, baseEventActorWeight, event, stateStore=Event.stateStore):
    state = stateStore[0]
    if event.name == "FriendHelpsInjury":
        if not actor.injured:  # there is nothing to heal...
            return 0, False
    return baseEventActorWeight, True

Event.registerInsertedCallback("modifyIndivActorWeights", checkActorInjured)

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.SetUninjured()
    state["allRelationships"].IncreaseFriendLevel(mainActor, participants[0], random.randint(3,4))
    state["allRelationships"].IncreaseLoveLevel(mainActor, participants[0], random.randint(0,2))
    desc = participants[0].name+' helped heal '+mainActor.name+"'s injury."
    return (desc, [participants[0], mainActor], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("FriendHelpsInjury", func)