
from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    theDead = [x for x in state["contestants"].values() if not x.alive]
    if not theDead:  # Need new event
        return None
    body = random.choice(theDead)
    tempList = [mainActor, body]
    mainActor.permStatChange({'stability': -1})
    if not body.inventory:
        desc = mainActor.name + ' found ' + body.name + \
            "'s body, but didn't find anything of value."
    else:
        lootList = Event.lootAll(mainActor, body)
        desc = mainActor.name + ' found ' + body.name + "'s body, "
        if lootList:
            desc += 'and looted ' + Event.englishList(lootList) + '.'
        else:
            desc += "but the body had nothing of value."
        tempList.extend(lootList)
    # Second entry is the contestants named in desc, in order. Third is anyone who died.
    return (desc, tempList, [])


Event.registerEvent("FindDeadBody", func)
