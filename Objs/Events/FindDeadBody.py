
from Objs.Events.Event import Event, EventOutput
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    theDead = [x for x in state["contestants"].values() if not x.alive]
    if not theDead:  # Need new event
        return None
    body = random.choice(theDead)
    tempList = [mainActor, body]
    mainActor.permStatChange({'stability': -1})
    lootDict = None
    if not body.inventory:
        desc = mainActor.name + ' found ' + body.name + \
            "'s body, but didn't find anything of value."
    else:
        lootDict = Event.lootAll(mainActor, body)
        desc = mainActor.name + ' found ' + body.name + "'s body, "
        if lootDict:
            desc += '.'
        else:
            desc += "but the body had nothing of value."
    # Second entry is the contestants named in desc, in order. Third is anyone who died.
    return EventOutput(desc, tempList, [], loot_table=lootDict)


Event.registerEvent("FindDeadBody", func)
