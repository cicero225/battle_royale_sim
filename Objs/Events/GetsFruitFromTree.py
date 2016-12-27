
from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None):
    mainActor.permStatChange({'endurance': 1})
    desc = mainActor.name+' collects fruit from a tree.'
    return (desc, [mainActor], []) # Second entry is the contestants named in desc, in order. Third is anyone who died.

Event.doEventGetsFruitFromTree= classmethod(func)

Event.registerEvent("GetsFruitFromTree", Event.doEventGetsFruitFromTree)

