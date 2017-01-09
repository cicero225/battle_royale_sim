from Objs.Events.Event import Event
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    victims[0].alive = False
    spearBroken = random.randint(0,1)
    if spearBroken:
        desc = mainActor.name+' threw a spear through '+victims[0].name+"'s neck and killed "+Event.parseGenderObject(victims[0])+". The spear was broken in the process."
        mainActor.removeItem(state["items"]["Spear"])
    else:
        desc = mainActor.name+' threw a spear through '+victims[0].name+"'s neck and killed "+Event.parseGenderObject(victims[0])+"."
    tempList = [mainActor, state["items"]["Spear"], victims[0]]
    lootList = Event.lootAll(mainActor, victims[0])
    if lootList:
        desc += ' '+mainActor.name+' looted the body for '+Event.englishList(lootList)+'.'
        tempList.extend(lootList)
    return (desc, tempList, [victims[0].name]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventThrowSpearKill = classmethod(func)

Event.registerEvent("ThrowSpearKill", Event.doEventThrowSpearKill)