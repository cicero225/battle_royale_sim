import warnings
from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.permStatChange({'stability': 3})
    desc = mainActor.name + " spends a night with " + participants[0].name
    try:
        del state["events"]["ShareIntimateConversation"].eventStore[mainActor.name]
    except:
        warnings.warn("I have no idea why this happens...")
    if participants[0].name in state["events"]["ShareIntimateConversation"].eventStore:
        participants[0].permStatChange({'stability': 3})
        del state["events"]["ShareIntimateConversation"].eventStore[participants[0].name]
        desc += " and they talk out their feelings."
    else:
        desc += " and resolves " + \
            Event.parseGenderPossessive(mainActor) + " confusion"
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, [mainActor, participants[0]], [])


Event.registerEvent("ResolvesFeelingConfusion", func)
