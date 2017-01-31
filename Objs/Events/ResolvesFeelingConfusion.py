
from Objs.Events.Event import Event

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.permStatChange({'stability': 3})
    desc = mainActor.name + " spends a night with "+participants[0].name
    print(state["events"]["ShareIntimateConversation"].eventStore) # temporary: there is a rare glitch here
    print(participants[0].name)
    print(participants[0].name in state["events"]["ShareIntimateConversation"].eventStore)
    state["events"]["ShareIntimateConversation"].eventStore[mainActor.name].clear()
    del state["events"]["ShareIntimateConversation"].eventStore[mainActor.name]
    if participants[0].name in state["events"]["ShareIntimateConversation"].eventStore:
        participants[0].permStatChange({'stability': 3})
        state["events"]["ShareIntimateConversation"].eventStore[participants[0].name].clear()
        del state["events"]["ShareIntimateConversation"].eventStore[participants[0].name]
        desc += " and they resolve their confusion."
    else:
        desc += " and resolves "+Event.parseGenderPossessive(mainActor)+" confusion"
    return (desc, [mainActor, participants[0]], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("ResolvesFeelingConfusion", func)
