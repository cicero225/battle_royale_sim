from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.permStatChange({'stability': -1,
                              'endurance': -3,
                              'combat ability': -3})
    desc = mainActor.name + " gets sick with a severe fever."
    if "SickWithFeverStore" not in state["callbackStore"]:
        state["callbackStore"]["SickWithFeverStore"] = {} 
    state["callbackStore"]["SickWithFeverStore"][mainActor.name] = (Event.activateEventNextTurnForContestant("RecoversFromFever", mainActor.name, state, 10), Event.activateEventNextTurnForContestant("DiesFromFever", mainActor.name, state, 10))
    return (desc, [mainActor], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventSickWithFever = classmethod(func)

Event.registerEvent("SickWithFever", Event.doEventSickWithFever)
