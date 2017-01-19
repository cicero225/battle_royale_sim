from Objs.Events.Event import Event
import random

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.addItem(state["items"]["Spear"])
    state["allRelationships"].IncreaseFriendLevel(mainActor, sponsors[0], random.randint(1,2))
    choice = random.randint(0,1)
    if choice:
        desc = sponsors[0].name+' gave a spear to '+mainActor.name+"."
        return (desc, [sponsors[0], state["items"]["Spear"], mainActor], [])
    else:
        desc = 'An unknown sponsor gave a spear to '+mainActor.name+"."
        return (desc, [state["items"]["Spear"], mainActor], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("SponsorGiveSpear", func)