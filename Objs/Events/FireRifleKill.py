from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    probKill = Event.DieOrEscapeProb1v1(mainActor, victims[0], state["settings"], defenseStat=(
        victims[0].getCombatAbility(mainActor) * 0.15 + victims[0].stats['cleverness'] * 0.10))
    tempList = [mainActor, state["items"]["Rifle"], victims[0]]
    # Deteriorate relationship of victim toward participant
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -2)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -3)
    # RNG ammo use, this is unique to the rifle.
    actualItem = mainActor.hasThing("Rifle")[0]
    currentAmmo = actualItem.data.get("currentammo", actualItem.rawData["ammo"])
    ammoUsed = min(random.randint(actualItem.rawData["ammouse"][0], actualItem.rawData["ammouse"][1]), currentAmmo)
    currentAmmo -= ammoUsed
    if random.random() < probKill:
        victims[0].kill()
        deadList = [victims[0].name]
        desc = mainActor.name + ' fired at ' + \
            victims[0].name + " from long range and killed " + \
            Event.parseGenderObject(victims[0]) + "."
        lootList = Event.lootAll(mainActor, victims[0])
        if lootList:
            desc += ' ' + mainActor.name + ' looted the body for ' + \
                Event.englishList(lootList) + '.'
            tempList.extend(lootList)
    else:
        deadList = []
        desc = mainActor.name + ' fired at ' + \
            victims[0].name + " from long range, but missed."
    if currentAmmo > 0:
        desc += "\nAmmo remaining: " + str(currentAmmo) + " (" + str(ammoUsed) + " used)"
        actualItem.data["currentammo"] = currentAmmo
    else:
        desc += "\nThe Rifle belonging to " + mainActor.name + " exhausted its ammo."
        mainActor.removeItem("Rifle")
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, tempList, deadList)


Event.registerEvent("FireRifleKill", func)
