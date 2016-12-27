from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None):
    mainActor.alive = False
    desc = mainActor.name + " died horribly of dysentary."
    return (desc, [mainActor.name], [mainActor.name]) # Second entry is the contestants named in desc, in order. Third is anyone who died. This is in strings.

Event.doEventDysentary = classmethod(func)

Event.registerEvent("Dysentary", Event.doEventDysentary)
