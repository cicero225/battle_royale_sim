
from Objs.Events.Event import Event
from Objs.Events.IndividualEventHandler import IndividualEventHandler
import random

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):    
    # Random relationship boost
    state["allRelationships"].IncreaseFriendLevel(mainActor, participants[0], random.randint(1,2)) 
    state["allRelationships"].IncreaseLoveLevel(mainActor, participants[0], random.randint(2,3))
    state["allRelationships"].IncreaseFriendLevel(participants[0], mainActor, random.randint(1,2))
    state["allRelationships"].IncreaseLoveLevel(participants[0], mainActor, random.randint(2,3))
    desc = mainActor.name+' and '+participants[0].name+' had an intimate conversation.'

    confused = []
    if mainActor.gender == participants[0].gender:
        if not random.randint(0,2):
            confused.append(mainActor)
            mainActor.permStatChange({'stability': -2})
        if not random.randint(0,2):
            confused.append(participants[0])
            participants[0].permStatChange({'stability': -2})
    if len(confused) == 2:
        desc += ' '+Event.englishList(confused)+' found themselves confused by their feelings.'
        weight = 10
    elif len(confused) == 1:
        desc += ' '+Event.englishList(confused)+' found '+Event.parseGenderReflexive(confused[0])+' confused by '+Event.parseGenderPossessive(confused[0])+' feelings.'
        weight = 20
    if confused:
        eventHandler = IndividualEventHandler(state)
        eventHandler.banEventForSingleContestant("ShareIntimateConversation", mainActor.name, state)
        eventHandler.banEventForSingleContestant("ShareIntimateConversation", participants[0].name, state)
        for person in confused:
            eventHandler.bindRoleForContestantAndEvent("participants", [mainActor if person != mainActor else participants[0]], person, "ResolvesFeelingConfusion")
            eventHandler.setEventWeightForSingleContestant("ResolvesFeelingConfusion", person.name, weight, state)
        self.eventStore[mainActor.name] = eventHandler
        self.eventStore[participants[0].name] = eventHandler # Yes, two copies
    return (desc, [mainActor, participants[0]], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings. 

Event.registerEvent("ShareIntimateConversation", func)
