from Objs.Events.Event import Event
import random

def checkParticipantMedicine(actor, participant, baseEventActorWeight, event):
    if event.name == "FriendGivesMedicine":
        for item in participant.inventory:
            if item.name == "Medicine":
                return baseEventActorWeight, True
        return 0, False
    return baseEventActorWeight, True

Event.registerInsertedCallback("modifyIndivActorWeightsWithParticipants", checkParticipantMedicine)

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.addItem(state["items"]["Medicine"])
    if not participants[0].removeItem(state["items"]["Medicine"]):
        raise AssertionError
    state["allRelationships"].IncreaseFriendLevel(mainActor, participants[0], random.randint(3,4))
    state["allRelationships"].IncreaseLoveLevel(mainActor, participants[0], random.randint(0,2))
    desc = participants[0].name+' gave Medicine to '+mainActor.name+" to help with "+Event.parseGenderPossessive(mainActor)+" fever."
    return (desc, [participants[0], state["items"]["Medicine"], mainActor], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("FriendGivesMedicine", func)