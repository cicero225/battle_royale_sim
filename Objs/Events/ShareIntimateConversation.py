
from Objs.Events.Event import Event
import random
from functools import partial

def onlyOneParticipant(requiredParticipant, relevantActor, eventName, contestantKey, thisevent, state, proceedAsUsual, participants, victims, sponsorsHere):
    if thisevent.name==eventName and relevantActor.name == contestantKey:
        del participants[:]
        participants.append(requiredParticipant)
    return proceedAsUsual

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):    
    # Random relationship boost
    state["allRelationships"].IncreaseFriendLevel(mainActor, participants[0], random.randint(1,2)) 
    state["allRelationships"].IncreaseLoveLevel(mainActor, participants[0], random.randint(2,3))
    state["allRelationships"].IncreaseFriendLevel(participants[0], mainActor, random.randint(1,2))
    state["allRelationships"].IncreaseLoveLevel(participants[0], mainActor, random.randint(2,3))
    desc = mainActor.name+' and '+participants[0].name+' had an intimate conversation.'

    confused = []
    if mainActor.gender == participants[0].gender:
        if not random.randint(0,1):
            confused.append(mainActor)
            mainActor.permStatChange({'stability': -2})
        if not random.randint(0,1):
            confused.append(participants[0])
            participants[0].permStatChange({'stability': -2})
    if len(confused) == 2:
        desc += ' '+Event.englishList(confused)+' found themselves confused by their feelings.'
        weight = 10
    elif len(confused) == 1:
        desc += ' '+Event.englishList(confused)+' found '+Event.parseGenderReflexive(confused[0])+' confused by '+Event.parseGenderPossessive(confused[0])+' feelings.'
        weight = 20
    for person in confused:
        state["callbackStore"].setdefault("ShareIntimateConversationConfusedStore", {})
        partipantFunc = partial(onlyOneParticipant, (mainActor if person != mainActor else participants[0]), person, "ResolvesFeelingConfusion")
        state["callbacks"]["overrideContestantEvent"].insert(0, partipantFunc)
        state["callbackStore"]["ShareIntimateConversationConfusedStore"][person.name] =(Event.activateEventNextTurnForContestant("ResolvesFeelingConfusion", person.name, state, weight), partipantFunc)
        state["callbackStore"]["ShareIntimateConversationConfusedStore"].setdefault('Banned', {})
        state["callbackStore"]["ShareIntimateConversationConfusedStore"]['Banned'].setdefault(mainActor.name, Event.activateEventNextTurnForContestant("ShareIntimateConversation", mainActor.name, state, 0))
        state["callbackStore"]["ShareIntimateConversationConfusedStore"]['Banned'].setdefault(participants[0].name, Event.activateEventNextTurnForContestant("ShareIntimateConversation", participants[0].name, state, 0))
    return (desc, [mainActor, participants[0]], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings. 

Event.doEventShareIntimateConversation = classmethod(func)

Event.registerEvent("ShareIntimateConversation", Event.doEventShareIntimateConversation)
