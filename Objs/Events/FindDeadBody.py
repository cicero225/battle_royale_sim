
from Objs.Events.Event import Event
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    theDead = [x for x in state["contestants"].values() if not x.alive]
    body = random.choice(theDead)
    if not body.inventory:
        desc = mainActor.name + ' found ' + body.name +"'s body, "
    else:
        lootList = Event.lootAll(mainActor, body)
        desc = mainActor.name + ' found ' + body.name +"'s body, "
        if lootList:
            desc += 'and looted '+Event.englishList(lootList)+'.'
        else:
            desc += "but didn't find anything of value."
    return (desc, [mainActor, body], []) # Second entry is the contestants named in desc, in order. Third is anyone who died.

Event.doEventFindDeadBody = classmethod(func)

Event.registerEvent("FindDeadBody", Event.doEventFindDeadBody)