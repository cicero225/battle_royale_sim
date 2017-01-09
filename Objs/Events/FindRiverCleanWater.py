from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.addItem(state["items"]["Clean Water"])
    desc = mainActor.name + " found a river with clean water, and collected some."
    return (desc, [mainActor, state["items"]["Clean Water"]], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventFindRiverCleanWater = classmethod(func)

Event.registerEvent("FindRiverCleanWater", Event.doEventFindRiverCleanWater)
