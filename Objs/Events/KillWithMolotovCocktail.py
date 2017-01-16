
from Objs.Events.Event import Event
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    probSurvival = (1-Event.DieOrEscapeProb1v1(mainActor, victims[0], state["settings"], defenseStat=(victims[0].stats['combat ability']*0.75+victims[0].stats['cleverness']*0.25)))*0.5 # This event is rigged against defender
    tempList = [mainActor, state["items"]["MolotovCocktail"], victims[0]]
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -4)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -6)
    if random.random()<probSurvival:
        desc = mainActor.name+' threw a molotov cocktail at '+victims[0].name+" but "+Event.parseGenderSubject(victims[0])+" escaped!"
        return (desc, tempList, [])
    else:
        victims[0].alive = False
        desc = mainActor.name+' threw a molotov cocktail at '+victims[0].name+" and burned "+Event.parseGenderObject(victims[0])+" alive."
        mainActor.permStatChange({'stability': -2})
        if mainActor.stats["stability"]<3:
            desc += " "+mainActor.name+" laughed at "+Event.parseGenderPossessive(victims[0])+" pain."
        mainActor.removeItem(state["items"]["MolotovCocktail"])
        lootList = Event.lootAll(mainActor, victims[0])
        if lootList:
            desc += ' '+mainActor.name+' looted the body for '+Event.englishList(lootList)+'.'
            tempList.extend(lootList)
        return (desc, tempList, [victims[0].name]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventKillWithMolotovCocktail = classmethod(func)

Event.registerEvent("KillWithMolotovCocktail", Event.doEventKillWithMolotovCocktail)