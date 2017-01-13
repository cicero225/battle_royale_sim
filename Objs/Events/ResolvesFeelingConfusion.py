
from Objs.Events.Event import Event

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.permStatChange({'stability': 3})
    desc = mainActor.name + " spends a night with "+participants[0].name
    state["callbacks"]["modifyIndivActorWeights"].remove(state["callbackStore"]["ShareIntimateConversationConfusedStore"][mainActor.name][0])
    state["callbacks"]["overrideContestantEvent"].remove(state["callbackStore"]["ShareIntimateConversationConfusedStore"][mainActor.name][1])
    del state["callbackStore"]["ShareIntimateConversationConfusedStore"][mainActor.name]
    if participants[0].name in state["callbackStore"]["ShareIntimateConversationConfusedStore"]:
        participants[0].permStatChange({'stability': 3})
        state["callbacks"]["modifyIndivActorWeights"].remove(state["callbackStore"]["ShareIntimateConversationConfusedStore"][participants[0].name][0])
        state["callbacks"]["overrideContestantEvent"].remove(state["callbackStore"]["ShareIntimateConversationConfusedStore"][participants[0].name][1])
        del state["callbackStore"]["ShareIntimateConversationConfusedStore"][participants[0].name]
        desc += " and they resolve their confusion."
    else:
        desc += " and resolves "+Event.parseGenderPossessive(mainActor)+" confusion"
    del state["callbackStore"]["ShareIntimateConversationConfusedStore"]['Banned'][mainActor.name]
    del state["callbackStore"]["ShareIntimateConversationConfusedStore"]['Banned'][participants[0].name]
    return (desc, [mainActor, participants[0]], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventResolvesFeelingConfusion = classmethod(func)

Event.registerEvent("ResolvesFeelingConfusion", Event.doEventResolvesFeelingConfusion)
