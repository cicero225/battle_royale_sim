
from Objs.Events.Event import Event
from ..Utilities.ArenaUtils import weightedDictRandom
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    numDead = random.randint(0,3)
    desc = mainActor.name+', '+participants[0].name+', and '+participants[1].name+' fought, '
    if not numDead:
        desc += 'but no one was hurt.'
        return(desc,[mainActor, participants[0], participants[1]], [])
    fightDict = {'main': 11-mainActor.stats['combat ability'],
    'part1': 11-participants[0].stats['combat ability'],
    'part2': 11-participants[1].stats['combat ability']}
    deadNames = weightedDictRandom(fightDict, numDead)
    desc += 'and '
    deadList = []
    for theDead in deadNames:
        if theDead == 'main':
            mainActor.alive = False
            deadList.append(mainActor)
        elif theDead == 'part1':
            participants[0].alive = False
            deadList.append(participants[0])
        elif theDead == 'part2':
            participants[1].alive = False
            deadList.append(participants[1])
    liveList = [x for x in participants+[mainActor] if x.alive ]
    descList = [mainActor, participants[0], participants[1]]
    if len(deadList) == 1:
        looter = liveList[random.randint(0,1)]
        lootList = Event.lootAll(looter, deadList[0])
        desc += deadList[0].name+' was killed!'
        if lootList:
            desc += ' '+looter.name+' looted the body for '+Event.englishList(lootList)+'.'
        descList.extend(lootList)
    elif len(deadList) == 2:
        lootList = Event.lootAll(liveList[0], deadList[0])
        lootList.extend(Event.lootAll(liveList[0], deadList[1]))
        desc += deadList[0].name+' and '+deadList[1].name+' were killed!'
        if lootList:
            desc += ' '+liveList[0].name+' looted the bodies for '+Event.englishList(lootList)+'.'
        descList.extend(lootList)
    elif len(deadList) == 3:
        desc += 'all three died in the fighting!'
    return (desc, descList, [x.name for x in deadList]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventThreeWayFight = classmethod(func)

Event.registerEvent("ThreeWayFight", Event.doEventThreeWayFight)
