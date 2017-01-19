
from Objs.Events.Event import Event

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.addItem(state["items"]["Spear"])
    desc = mainActor.name+' crafted a crude spear.'
    return (desc, [mainActor, state["items"]["Spear"]], []) # Second entry is the contestants named in desc, in order. Third is anyone who died.

Event.registerEvent("CraftSpear", func)