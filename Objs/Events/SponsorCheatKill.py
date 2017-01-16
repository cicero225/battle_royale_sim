
from Objs.Events.Event import Event
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.alive = False
    if random.randint(0,1):
        desc = sponsors[0].name+' cheated, killing '+mainActor.name + " while no one was looking."
        tempList = [sponsors[0], mainActor]
    else:
        desc = 'An unknown sponsor cheated, killing '+mainActor.name + " while no one was looking."
        tempList = [mainActor]
    return (desc, tempList, [mainActor.name]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventSponsorCheatKill = classmethod(func)

Event.registerEvent("SponsorCheatKill", Event.doEventSponsorCheatKill)