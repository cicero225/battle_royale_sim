from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = mainActor.name+' did absolutely nothing.'
    return (desc, [mainActor], []) # Second entry is the contestants named in desc, in order. Third is anyone who died.

Event.doEventEventTemplate = classmethod(func)

Event.registerEvent("EventTemplate", Event.doEventEventTemplate)

