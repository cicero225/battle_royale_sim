
from Objs.Events.Event import Event
import random

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = mainActor.name+' invited '+str(victims[0])+' up to the top of a gorge to admire the view, but betrayed '+Event.parseGenderObject(victims[0])+', pushing '+Event.parseGenderObject(victims[0])+' off the cliff to '+Event.parseGenderPossessive(victims[0])+' death.'
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -4)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -6)
    victims[0].alive = False
    if mainActor.stats["stability"]<3:
        desc +=' '+Event.parseGenderSubject(mainActor).capitalize()+' smiled as '+Event.parseGenderSubject(mainActor)+' watched '+Event.parseGenderObject(victims[0])+' fall.'
        mainActor.permStatChange({'stability': -1})
    tempList = [mainActor, victims[0]]
    return (desc, tempList, [victims[0].name]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("BetrayPushOffCliff", func)