
from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    # Deteriorate relationship of victim toward participant
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -2)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -3)
    probKill = Event.DieOrEscapeProb1v1(mainActor, victims[0], state["settings"], defenseStat=(
        victims[0].stats['combat ability'] + victims[0].stats['cleverness'] * 0.5))  # this event is mildly rigged against attacker
    if random.random() < probKill:
        victims[0].alive = False
        if mainActor.stats['ruthlessness'] > 6:
            desc = mainActor.name + ' assaulted ' + \
                victims[0].name + ', killing ' + \
                Event.parseGenderObject(victims[0]) + ' brutally.'
        else:
            desc = mainActor.name + ' attacked ' + \
                victims[0].name + ', killing ' + \
                Event.parseGenderObject(victims[0]) + '.'
        return (desc, [mainActor, victims[0]], [victims[0].name])
    else:
        desc = mainActor.name + ' tried to attack ' + \
            victims[0].name + ', but ' + \
            Event.parseGenderSubject(victims[0]) + ' managed to escape.'
        # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
        return (desc, [mainActor, victims[0]], [])


Event.registerEvent("AAttacksB", func)
