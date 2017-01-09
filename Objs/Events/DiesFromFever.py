from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = mainActor.name + " dies from "+Event.parseGenderPossessive(mainActor)+" fever!"
    mainActor.alive = False
    state["callbacks"]["modifyIndivActorWeights"].remove(state["callbackStore"]["SickWithFeverStore"][mainActor.name][0])
    state["callbacks"]["modifyIndivActorWeights"].remove(state["callbackStore"]["SickWithFeverStore"][mainActor.name][1])
    del state["callbackStore"]["SickWithFeverStore"][mainActor.name]
    return (desc, [mainActor], [mainActor.name]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventDiesFromFever = classmethod(func)

Event.registerEvent("DiesFromFever", Event.doEventDiesFromFever)
