from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.permStatChange({'stability': 1,
                              'endurance': 3,
                              'combat ability': 3})
    desc = mainActor.name + " recovers from "+Event.parseGenderPossessive(mainActor)+" fever."
    state["callbacks"]["modifyIndivActorWeights"].remove(state["callbackStore"]["SickWithFeverStore"][mainActor.name][0])
    state["callbacks"]["modifyIndivActorWeights"].remove(state["callbackStore"]["SickWithFeverStore"][mainActor.name][1])
    del state["callbackStore"]["SickWithFeverStore"][mainActor.name]
    return (desc, [mainActor.name], []) # Second entry is the contestants named in desc, in order. Third is anyone who died. This is in strings.

Event.doEventRecoversFromFever = classmethod(func)

Event.registerEvent("RecoversFromFever", Event.doEventRecoversFromFever)
