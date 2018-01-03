
from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.addItem(state["items"]["Fruit"])
    desc = mainActor.name + ' collected fruit from a tree.'
    # Second entry is the contestants named in desc, in order. Third is anyone who died.
    return (desc, [mainActor, state["items"]["Fruit"]], [])


Event.registerEvent("GetsFruitFromTree", func)
