
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

    if random.random() < detection:
        # Participant realizes what's going on
        desc += str(victims[0]) + " caught " + \
            Event.parseGenderObject(mainActor) + " in the act and attacked!"
        (fightDesc, fightDescList, fightDeadList, allKillers) = Event.fight(
            descList, state["allRelationships"], state["settings"])
        # Special: if only one loser, 33% chance the loser escapes injured instead, losing loot. If they are already injured they just die (skip this segment).
        if len(fightDeadList) == 1 and random.random() < 0.33 and not fightDeadList[0].hasThing("Injury"):
            # revive the loser
            fightDeadList[0].alive = True
            fightDeadList[0].addStatus(state["statuses"]["Injury"])
            if fightDeadList[0] == mainActor:
                desc += ' In the end, ' + mainActor.name + ' was injured and forced to flee.'
                if fightDescList:
                    desc += ' ' + Event.parseGenderSubject(mainActor).capitalize(
                    ) + ' left behind ' + Event.englishList(fightDescList) + '.'
            else:
                desc += ' In the end, however, ' + \
                    victims[0].name + ' was injured and forced to flee.'
                if fightDescList:
                    desc += ' ' + Event.parseGenderSubject(victims[0]).capitalize(
                    ) + ' left behind ' + Event.englishList(fightDescList) + '.'
            descList.extend(fightDescList)
            return (desc, descList, [])

        if not fightDeadList:
            desc += ' The fight was a draw, and the two sides departed, friends no more.'
            return (desc, descList, [])
        desc += " " + fightDesc[4:].capitalize()
        descList += fightDescList
        return (desc, descList, [x.name for x in fightDeadList], allKillers)

    else:
        desc += str(victims[0]) + \
            " ate the meal, blissfully unaware, before falling over dead."
        victims[0].alive = False
        lootList = Event.lootAll(mainActor, victims[0])
        if lootList:
            desc += ' ' + str(mainActor) + ' looted ' + Event.englishList(lootList) + '.'
            descList.extend(lootList)

    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, descList, [str(victims[0])])


Event.registerEvent("ACooksForBButPoison", func)
