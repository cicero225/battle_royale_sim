
from Objs.Events.Event import Event
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    # Hmm...having an object that takes care of this max 5 business would be nice    
    # Deteriorate relationship of victim toward participant
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -2)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -3)
    probKill = Event.DieOrEscapeProb1v1(mainActor, victims[0], state["settings"], defenseStat=(victims[0].stats['combat ability']+victims[0].stats['cleverness']*0.5)) # this event is mildly rigged against attacker
    if random.random()<probKill:
        victims[0].alive = False
        desc = mainActor.name+' attacked '+victims[0].name+' with '+Event.parseGenderPossessive(mainActor)+' bare fists, killing '+Event.parseGenderObject(victims[0])+' brutally.'
        return (desc, [mainActor, victims[0]], [victims[0].name])
    else:
        desc = mainActor.name+' attacked '+victims[0].name+' with '+Event.parseGenderPossessive(mainActor)+' bare fists, but '+Event.parseGenderSubject(victims[0])+' escaped.'
        return (desc, [mainActor, victims[0]], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventAAttacksB = classmethod(func)

Event.registerEvent("AAttacksB", Event.doEventAAttacksB)
