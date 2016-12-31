from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.removeItem(state["items"]["Clean Water"])
    desc = mainActor.name + " ran out of clean water."
    return (desc, [mainActor.name], []) # Second entry is the contestants named in desc, in order. Third is anyone who died. This is in strings.

Event.doEventOutOfCleanWater = classmethod(func)

Event.registerEvent("OutOfCleanWater", Event.doEventOutOfCleanWater)
