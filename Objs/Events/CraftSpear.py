
from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.addItem(state["items"]["Spear"])
    desc = mainActor.name + ' crafted a crude spear.'
    # Second entry is the contestants named in desc, in order. Third is anyone who died.
    return (desc, [mainActor, state["items"]["Spear"]], [])


Event.registerEvent("CraftSpear", func)
