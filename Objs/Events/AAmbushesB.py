
from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    # Deteriorate relationship of victim toward participant
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -2)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -3)
    probKill = Event.DieOrEscapeProb1v1(mainActor, victims[0], state["settings"], defenseStat=(
        victims[0].getCombatAbility(mainActor) * 0.5 + victims[0].stats['cleverness']))  # this event is mildly rigged against attacker
    descList = [mainActor, victims[0]]
    if random.random() < probKill:
        victims[0].kill()
        if mainActor.stats['ruthlessness'] > 6:
            desc = mainActor.name + ' lay in wait for ' + \
                victims[0].name + ', surprising and gutting ' + \
                Event.parseGenderObject(victims[0]) + '.'
        else:
            desc = mainActor.name + ' lay in wait for ' + \
                victims[0].name + ', surprising and killing ' + \
                Event.parseGenderObject(victims[0]) + '.'
        lootList = Event.lootAll(mainActor, victims[0])
        if lootList:
            desc += ' ' + str(mainActor) + ' looted ' + Event.englishList(lootList) + '.'
            descList.extend(lootList)
        return (desc, descList, [victims[0].name])
    else:
        desc = mainActor.name + ' lay in wait for ' + \
            victims[0].name + ', but ' + \
            Event.parseGenderSubject(victims[0]) + ' managed to see it coming.'
        # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
        return (desc, descList, [])


Event.registerEvent("AAmbushesB", func)
