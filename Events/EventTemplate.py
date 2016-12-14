from Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None):
    pass

Event.doEventEventTemplate = classmethod(func)

Event.registerEvent("EventTemplate", Event.doEventEventTemplate)

