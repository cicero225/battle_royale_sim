from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None):
    mainActor.addItem(state["items"]["Clean Water"])
    desc = mainActor.name + " found a river with clean water, and collected some."
    return (desc, [mainActor.name], []) # Second entry is the contestants named in desc, in order. Third is anyone who died. This is in strings.

Event.doEventFindRiverCleanWater = classmethod(func)

Event.registerEvent("FindRiverCleanWater", Event.doEventFindRiverCleanWater)
