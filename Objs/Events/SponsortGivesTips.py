from Objs.Events.Event import Event
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    state["allRelationships"].IncreaseFriendLevel(mainActor, sponsors[0], random.randint(2, 3))
    mainActor.permStatChange({'survivalism': 2,
                              'cleverness': 2})
    choice = random.randint(0,1)
    if choice:
        desc = sponsors[0].name+' gave a map and a book of instructions to '+mainActor.name+"."
        return (desc, [sponsors[0], mainActor], [])
    else:
        desc = 'An unknown sponsor gave a map and a book of instructions to '+mainActor.name+"."
        return (desc, [mainActor], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventSponsorGivesTips = classmethod(func)

Event.registerEvent("SponsorGivesTips", Event.doEventSponsorGivesTips)