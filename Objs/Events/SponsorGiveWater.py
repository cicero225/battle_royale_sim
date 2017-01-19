from Objs.Events.Event import Event
import random

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.addItem(state["items"]["Clean Water"])
    state["allRelationships"].IncreaseFriendLevel(mainActor, sponsors[0], random.randint(1,2))
    choice = random.randint(0,1)
    if choice:
        desc = sponsors[0].name+' gave clean water to '+mainActor.name+"."
        return (desc, [sponsors[0], state["items"]["Clean Water"], mainActor], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    else:
        desc = 'An unknown sponsor gave clean water to '+mainActor.name+"."
        return (desc, [state["items"]["Clean Water"], mainActor], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("SponsorGiveWater", func)