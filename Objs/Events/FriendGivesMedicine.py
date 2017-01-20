from Objs.Events.Event import Event
import random

def startup(state):
    def func(actor, participant, baseEventActorWeight, event):
        if state["items"]["Medicine"] in participant.inventory:
            return baseEventActorWeight, True
        return 0, False
    state["callbacks"]["modifyIndivActorWeightsWithParticipants"].append(func)  # It's okay not to anonymize this one

Event.registerStartup("FriendGivesMedicine", startup)

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.addItem(state["items"]["Medicine"])
    if not participants[0].removeItem(state["items"]["Medicine"]):
        raise AssertionError
    state["allRelationships"].IncreaseFriendLevel(mainActor, participants[0], random.randint(3,4))
    state["allRelationships"].IncreaseLoveLevel(mainActor, participants[0], random.randint(0,2))
    desc = participants[0].name+' gave Medicine to '+mainActor.name+" to help with "+Event.parseGenderPossessive(mainActor)+" fever."
    return (desc, [participants[0], state["items"]["Medicine"], mainActor], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("FriendGivesMedicine", func)