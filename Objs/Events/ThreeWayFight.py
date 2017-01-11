
from Objs.Events.Event import Event
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    numDead = random.randint(0,3)
    desc = mainActor.name+', '+participants[0].name+', and '+participants[1].name+' fought, '
    descList = [mainActor, participants[0], participants[1]]
    fightDesc, fightList, fightDead = Event.fight(descList)
    return (desc+fightDesc, descList+fightList, [x.name for x in fightDead]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventThreeWayFight = classmethod(func)

Event.registerEvent("ThreeWayFight", Event.doEventThreeWayFight)
