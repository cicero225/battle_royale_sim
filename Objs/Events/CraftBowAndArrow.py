import random

from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    probSuccess = mainActor.stats["cleverness"] * \
        0.03 + mainActor.stats["survivalism"] * 0.03
    descList = [mainActor]
    if random.random() < probSuccess:
        mainActor.addItem(state["items"]["Bow and Arrow"], isNew=True)
        descList.append(state["items"]["Bow and Arrow"])
        desc = mainActor.name + ' crafted a Bow and Arrow set.'
    else:
        desc = mainActor.name + ' tried crafting a Bow and Arrow set, but failed.'
    # Second entry is the contestants named in desc, in order. Third is anyone who died.
    return (desc, descList, [])


Event.registerEvent("CraftBowAndArrow", func)
