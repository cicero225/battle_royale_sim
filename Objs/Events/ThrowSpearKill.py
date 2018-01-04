from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    probKill = Event.DieOrEscapeProb1v1(mainActor, victims[0], state["settings"], defenseStat=(
        victims[0].stats['combat ability'] * 0.75 + victims[0].stats['cleverness'] * 0.25))
    spearBroken = random.randint(0, 1)
    tempList = [mainActor, state["items"]["Spear"], victims[0]]
    # Deteriorate relationship of victim toward participant
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -2)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -3)
    if random.random() < probKill:
        victims[0].alive = False
        deadList = [victims[0].name]
        desc = mainActor.name + ' threw a spear through ' + \
            victims[0].name + "'s neck and killed " + \
            Event.parseGenderObject(victims[0]) + "."
        lootList = Event.lootAll(mainActor, victims[0])
        if lootList:
            desc += ' ' + mainActor.name + ' looted the body for ' + \
                Event.englishList(lootList) + '.'
            tempList.extend(lootList)
    else:
        deadList = []
        desc = mainActor.name + ' threw a spear at ' + \
            victims[0].name + ", but missed."
    if spearBroken:
        desc += " The spear was broken in the process."
        mainActor.removeItem(state["items"]["Spear"])
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, tempList, deadList)


Event.registerEvent("ThrowSpearKill", func)
