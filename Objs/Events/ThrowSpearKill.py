from Objs.Contestants.Contestant import Contestant
from Objs.Utilities.ArenaEnumsAndNamedTuples import EventOutput
from Objs.Events.Event import Event, EventOutput

import random
from typing import List, Optional


def func(self: Event, mainActor: Contestant, state, participants: Optional[List[Contestant]], victims: List[Contestant], sponsors: Optional[List[Contestant]]=None):
    probKill = Event.DieOrEscapeProb1v1(mainActor, victims[0], state["settings"], defenseStat=(
        victims[0].getCombatAbility(mainActor) * 0.75 + victims[0].stats['cleverness'] * 0.25))
    spearBroken = random.randint(0, 1)
    tempList = [mainActor, state["items"]["Spear"], victims[0]]
    # Deteriorate relationship of victim toward participant
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -2)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -3)
    lootDict = None
    destroyedList = None
    if random.random() < probKill:
        victims[0].kill()
        deadList = [victims[0].name]
        desc = mainActor.name + ' threw a spear through ' + \
            victims[0].name + "'s neck and killed " + \
            Event.parseGenderObject(victims[0]) + "."
        lootDict, destroyedList = self.lootForOne(mainActor, victims[0])
    else:
        deadList = []
        desc = mainActor.name + ' threw a spear at ' + \
            victims[0].name + ", but missed."
        # 50/50 chance the victim gets the spear, if not broken.
        if not spearBroken and random.randint(0, 1):
            input()
            desc += " " + victims[0].name + " was able to steal the spear!"
            lootref = mainActor.removeAndGet(state["items"]["Spear"])
            victims[0].addItem(lootref)
            lootDict = {victims[0].name: [lootref]}
    if spearBroken:
        desc += " The spear was broken in the process."
        mainActor.removeItem(state["items"]["Spear"])
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return EventOutput(desc, tempList, deadList, loot_table=lootDict, destroyed_loot_table=destroyedList)


Event.registerEvent("ThrowSpearKill", func)
