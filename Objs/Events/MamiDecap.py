from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.alive = False
    desc = mainActor.name + " was decapitated by a trap due to carelessness and wanting to show off."
    return (desc, [mainActor.name], [mainActor.name]) # Second entry is the contestants named in desc, in order. Third is anyone who died. This is in strings.

Event.doEventMamiDecap = classmethod(func)

Event.registerEvent("MamiDecap", Event.doEventMamiDecap)
