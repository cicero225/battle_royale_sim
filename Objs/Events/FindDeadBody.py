
from Objs.Events.Event import Event
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    theDead = [x for x in state["contestants"].values() if not x.alive]
    body = random.choice(theDead)
    tempList = [mainActor, body]
    if not body.inventory:
        desc = mainActor.name + ' found ' + body.name +"'s body, but didn't find anything of value."
    else:
        lootList = Event.lootAll(mainActor, body)
        desc = mainActor.name + ' found ' + body.name +"'s body, "
        if lootList:
            desc += 'and looted '+Event.englishList(lootList)+'.'
        else:
            desc += "but the body had nothing of value."
        tempList.extend(lootList)
    return (desc, tempList, []) # Second entry is the contestants named in desc, in order. Third is anyone who died.

Event.doEventFindDeadBody = classmethod(func)

Event.registerEvent("FindDeadBody", Event.doEventFindDeadBody)