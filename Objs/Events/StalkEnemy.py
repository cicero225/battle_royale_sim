from Objs.Events.Event import Event
import random

def checkParticipantLove(actor, participant, baseEventActorWeight, event):
    if event.name != "StalkEnemy":
        return baseEventActorWeight, True
    possible_love = actor.hasThing("Love")
    if not possible_love or str(possible_love[0].target) != str(participant):    
        return baseEventActorWeight, True
    return 0, False

Event.registerInsertedCallback(
    "modifyIndivActorWeightsWithParticipants", checkParticipantLove)

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = mainActor.name + ' stalked ' + \
        victims[0].name + ' from the shadows, building an understanding of ' + Event.parseGenderPossessive(victims[0]) + ' behavior and skills.'
    mainActor.addItem(state["items"]["Dossier"], isNew=True, target=victims[0])
    
    descList = [mainActor, victims[0]]
    # If it's evening, mainActor gains hypothermia from not making a fire.
    if state["curPhase"] == "Evening":
        desc += " However, " + Event.parseGenderSubject(mainActor) + " sacrificed " + Event.parseGenderPossessive(mainActor) + " ability to make a fire, and became hypothermic."
        descList.append(state["statuses"]["Hypothermia"])
        mainActor.addStatus("Hypothermia")
    
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, descList, [], None, [mainActor])


Event.registerEvent("StalkEnemy", func)