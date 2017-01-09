from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.alive = False
    desc = mainActor.name + " died horribly of dysentary."
    return (desc, [mainActor], [mainActor.name]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventDysentary = classmethod(func)

Event.registerEvent("Dysentary", Event.doEventDysentary)
