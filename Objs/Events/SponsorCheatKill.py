
from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.kill()
    if random.randint(0, 1):
        desc = sponsors[0].name + ' cheated, killing ' + \
            mainActor.name + " while no one was looking."
        tempList = [sponsors[0], mainActor]
    else:
        desc = 'An unknown sponsor cheated, killing ' + \
            mainActor.name + " while no one was looking."
        tempList = [mainActor]
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, tempList, [mainActor.name])


Event.registerEvent("SponsorCheatKill", func)
