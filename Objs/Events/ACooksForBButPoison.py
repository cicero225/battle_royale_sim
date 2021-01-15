
from Objs.Utilities.ArenaEnumsAndNamedTuples import EventOutput
from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = str(mainActor) + " offered to cook for " + \
        str(victims[0]) + ", who gladly accepted."
    descList = [mainActor, victims[0]]

    # Roll for failure to actually poison
    notFailure = (victims[0].stats["cleverness"] +
                  victims[0].stats["survivalism"]) / 15
    if random.random() > notFailure:
        desc += " However, " + \
            str(mainActor) + " tried to secretly poison the dish, but failed, using the wrong mushrooms. The dish was delicious."
        state["allRelationships"].IncreaseFriendLevel(
            victims[0], mainActor, random.randint(1, 3))
        state["allRelationships"].IncreaseLoveLevel(
            victims[0], mainActor, random.randint(0, 2))
        return (desc, descList, [])

    desc += " However, " + str(mainActor) + \
        " tried to secretly poison the dish! "

    # Roll for participant realizing what's going on
    detection = (victims[0].stats["cleverness"] +
                 victims[0].stats["survivalism"]) / 30

    injuries = None
    destroyedList = None
    if random.random() < detection:
        # Participant realizes what's going on
        desc += str(victims[0]) + " caught " + \
            Event.parseGenderObject(mainActor) + " in the act and attacked!"
        (fightDesc, fightDeadList, allKillers, lootDict, injuries, destroyedList) = self.fight(
            descList, state["allRelationships"])
        # Special: if only one loser, 33% chance the loser escapes injured instead, losing loot. If they are already injured they just die (skip this segment).
        if len(fightDeadList) == 1 and random.random() < 0.33 and not fightDeadList[0].hasThing("Injury"):
            # revive the loser
            fightDeadList[0].alive = True
            fightDeadList[0].addStatus(state["statuses"]["Injury"])
            if fightDeadList[0] == mainActor:
                desc += ' In the end, ' + mainActor.name + ' was injured and forced to flee.'
            else:
                desc += ' In the end, however, ' + \
                    victims[0].name + ' was injured and forced to flee.'
            return EventOutput(desc, descList, [], loot_table=lootDict, injuries=injuries, destroyed_loot_table=destroyedList)

        if not fightDeadList:
            desc += ' The fight was a draw, and the two sides departed, friends no more.'
            return (desc, descList, [])
        desc += fightDesc
        return (desc, descList, [x.name for x in fightDeadList], allKillers)

    else:
        desc += str(victims[0]) + \
            " ate the meal, blissfully unaware, before falling over dead."
        victims[0].kill()
        lootDict, destroyedList = self.lootForOne(mainActor, victims[0], chanceDestroyedOverride=0)

    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return EventOutput(desc, descList, [str(victims[0])], loot_table=lootDict, injuries=injuries, destroyed_loot_table=destroyedList)


Event.registerEvent("ACooksForBButPoison", func)
