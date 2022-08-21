
from Objs.Utilities.ArenaEnumsAndNamedTuples import EventOutput
from Objs.Contestants.Contestant import Contestant
from Objs.Events.Event import Event
from typing import List, Optional
import random


def func(self: Event, mainActor: Contestant, state=None, participants=None, victims: Optional[List[Contestant]]=None, sponsors=None):
    if victims is None:
        raise NotImplementedError()
    probSurvival = (1 - Event.DieOrEscapeProb1v1(mainActor, victims[0], state["settings"], defenseStat=(
        victims[0].getCombatAbility(mainActor) * 0.75 + victims[0].stats['cleverness'] * 0.25))) * 0.5  # This event is rigged against defender
    tempList = [mainActor, state["items"]["MolotovCocktail"], victims[0]]
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -4)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -6)
    if random.random() < probSurvival:
        desc = mainActor.name + ' threw a molotov cocktail at ' + \
            victims[0].name + " but " + \
            Event.parseGenderSubject(victims[0]) + " escaped!"
        return (desc, tempList, [])
    else:
        victims[0].kill()
        desc = mainActor.name + ' threw a molotov cocktail at ' + \
            victims[0].name
        if victims[0].hasThing("Explosives") and random.random() > 0.5:
            desc += f'. But {victims[0]} was carrying Explosives, and the explosion also killed {mainActor}!'  
            mainActor.removeItem(state["items"]["MolotovCocktail"])
            victims[0].removeStatus(state["statuses"]["Hypothermia"])
            lootDict, destroyedList = self.lootForOne(mainActor, victims[0], 1)
            lootDict, secondList = self.lootForOne(mainActor, mainActor, 1)
            destroyedList.extend(secondList)
            mainActor.removeStatus(state["statuses"]["Hypothermia"])
            mainActor.kill()
            return EventOutput(desc, tempList, [mainActor.name, victims[0].name], loot_table=lootDict, destroyed_loot_table=destroyedList)
        desc += " and burned " + \
            Event.parseGenderObject(victims[0]) + " alive."
        mainActor.permStatChange({'stability': -2})
        if mainActor.stats["stability"] < 3:
            desc += " " + mainActor.name + " laughed at " + \
                Event.parseGenderPossessive(victims[0]) + " agony."
        mainActor.removeItem(state["items"]["MolotovCocktail"])
        lootDict, destroyedList = self.lootForOne(mainActor, victims[0], 1)
        if victims[0].removeStatus(state["statuses"]["Hypothermia"]):
            desc += " " + victims[0].name + " is no longer hypothermic."
        # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
        return EventOutput(desc, tempList, [victims[0].name], loot_table=lootDict, destroyed_loot_table=destroyedList)


Event.registerEvent("KillWithMolotovCocktail", func)
