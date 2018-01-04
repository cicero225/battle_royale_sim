
from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    # Random relationship boost
    state["allRelationships"].IncreaseFriendLevel(
        mainActor, participants[0], random.randint(0, 2))
    state["allRelationships"].IncreaseLoveLevel(
        mainActor, participants[0], random.randint(0, 1))
    state["allRelationships"].IncreaseFriendLevel(
        participants[0], mainActor, random.randint(0, 2))
    state["allRelationships"].IncreaseLoveLevel(
        participants[0], mainActor, random.randint(0, 1))
    desc = mainActor.name + ' and ' + \
        participants[0].name + ' shared stories about their lives.'
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, [mainActor, participants[0]], [])


Event.registerEvent("ShareStoryofLife", func)
