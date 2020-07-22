
from Objs.Events.Event import Event, EventOutput
import random

# future thoughts:
#    if someone finds the dead body of their friend/lover (is this possible?), then effect and message should be different


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    theDead = [x for x in state["contestants"].values() if not x.alive]
    
    # if no one dead, then no body to find, so need new event
    if not theDead:  
        return None

    # encounter random body… this might be a problem if bodies ever get incinerated or something?
    body = random.choice(theDead)
    mainActor.permStatChange({'stability': -1})
    
    # initialize some stuff
    lootDict = None
    descBeginning = mainActor.name + ' found ' + body.name + "'s body"
    descNoLoot = descBeginning + ', but searching it turned up nothing useful'
    descEnd = '.'

    # generate appropriate message
    if body.inventory:
        lootDict = Event.lootForOne(mainActor, body)
        if lootDict:
            # if there's any loot, a separate message will be generated for it, so we don't need to describe it here
            desc = descBeginning 
        else:
            desc = descNoLoot
    else:
        desc = descNoLoot
    desc += descEnd

    # Second entry is the contestants named in desc, in order. Third is anyone who died… but no one died.
    return EventOutput(desc, [mainActor, body], [], loot_table=lootDict)


Event.registerEvent("FindDeadBody", func)
