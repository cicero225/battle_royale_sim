from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = mainActor.name+' hunts for others to kill.'
    return (desc, [mainActor], []) # Second entry is the contestants named in desc, in order. Third is anyone who died.

Event.doEventHuntsForOthers = classmethod(func)

Event.registerEvent("HuntsForOthers", Event.doEventHuntsForOthers)

