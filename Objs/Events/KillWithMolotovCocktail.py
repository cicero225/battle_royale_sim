
from Objs.Utilities.ArenaEnumsAndNamedTuples import EventOutput
from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
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
            victims[0].name + " and burned " + \
            Event.parseGenderObject(victims[0]) + " alive."
        mainActor.permStatChange({'stability': -2})
        if mainActor.stats["stability"] < 3:
            desc += " " + mainActor.name + " laughed at " + \
                Event.parseGenderPossessive(victims[0]) + " agony."
        mainActor.removeItem(state["items"]["MolotovCocktail"])
        lootDict = Event.lootForOne(mainActor, victims[0])
        # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
        return EventOutput(desc, tempList, [victims[0].name], loot_table=lootDict)


Event.registerEvent("KillWithMolotovCocktail", func)
