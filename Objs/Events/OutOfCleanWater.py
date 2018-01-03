import random
from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.removeItem(state["items"]["Clean Water"])

    if random.randint(1, 2) == 1:
        desc = mainActor.name + " ran out of " + \
            state["items"]["Clean Water"].friendly + "."
    else:
        desc = mainActor.name + "'s " + \
            state["items"]["Clean Water"].friendly + " was tainted by dirt."
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, [mainActor, state["items"]["Clean Water"]], [])


Event.registerEvent("OutOfCleanWater", func)
