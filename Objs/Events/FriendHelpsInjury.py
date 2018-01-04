from Objs.Events.Event import Event
from collections import defaultdict
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.removeStatus(state["statuses"]["Injury"])
    state["allRelationships"].IncreaseFriendLevel(
        mainActor, participants[0], random.randint(3, 4))
    state["allRelationships"].IncreaseLoveLevel(
        mainActor, participants[0], random.randint(0, 2))
    desc = participants[0].name + ' helped heal ' + \
        mainActor.name + "'s injury."
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, [participants[0], mainActor], [])


Event.registerEvent("FriendHelpsInjury", func)
