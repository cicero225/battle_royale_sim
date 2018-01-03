from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    probKill = Event.DieOrEscapeProb1v1(mainActor, victims[0], state["settings"], defenseStat=(
        victims[0].stats['combat ability'] * 0.25 + victims[0].stats['cleverness'] * 0.15))
    tempList = [mainActor, state["items"]["Bow and Arrow"], victims[0]]
    # Deteriorate relationship of victim toward participant
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -2)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -3)
    if random.random() < probKill:
        victims[0].alive = False
        deadList = [victims[0].name]
        desc = mainActor.name + ' shot an arrow at ' + \
            victims[0].name + " and killed " + \
            Event.parseGenderObject(victims[0]) + "."
        lootList = Event.lootAll(mainActor, victims[0])
        if lootList:
            desc += ' ' + mainActor.name + ' looted the body for ' + \
                Event.englishList(lootList) + '.'
            tempList.extend(lootList)
    else:
        deadList = []
        desc = mainActor.name + ' shot an arrow at ' + \
            victims[0].name + ", but missed."
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, tempList, deadList)


Event.registerEvent("FireArrowKill", func)
