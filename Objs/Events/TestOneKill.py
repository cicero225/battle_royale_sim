from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    victims[0].alive = False
    desc = mainActor.name+' killed '+victims[0].name+"."
    return (desc, [mainActor.name, victims[0].name], [victims[0].name]) # Second entry is the contestants named in desc, in order. Third is anyone who died. This is in strings.

Event.doEventTestOneKill = classmethod(func)

Event.registerEvent("TestOneKill", Event.doEventTestOneKill)
