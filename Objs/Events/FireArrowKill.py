from Objs.Utilities.ArenaEnumsAndNamedTuples import EventOutput
from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    probKill = Event.DieOrEscapeProb1v1(mainActor, victims[0], state["settings"], defenseStat=(
        victims[0].getCombatAbility(mainActor) * 0.25 + victims[0].stats['cleverness'] * 0.15))
    tempList = [mainActor, state["items"]["Bow and Arrow"], victims[0]]
    # Deteriorate relationship of victim toward participant
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -2)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -3)
    lootDict = None
    destroyedList = None
    if random.random() < probKill:
        victims[0].kill()
        deadList = [victims[0].name]
        desc = mainActor.name + ' shot an arrow at ' + \
            victims[0].name + " and killed " + \
            Event.parseGenderObject(victims[0]) + "."
        lootDict, destroyedList = self.lootForOne(mainActor, victims[0])
    else:
        deadList = []
        desc = mainActor.name + ' shot an arrow at ' + \
            victims[0].name + ", but missed."
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return EventOutput(desc, tempList, deadList, loot_table=lootDict, destroyed_loot_table=destroyedList)


Event.registerEvent("FireArrowKill", func)
