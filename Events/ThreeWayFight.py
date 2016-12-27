
from Events.Event import Event
from ..Utilities.ArenaUtils import weightedDictRandom

def func(Event, mainActor, state=None, participants=None, victims=None):
    numDead = random.randint(0,3)
    desc = mainActor.name+', '+participants[0].name+', and '+participants[1].name+' fought, '
    if not numDead:
        desc += 'but no one was hurt.'
        return(desc,[mainActor.name, participants[0].name, participants[1].name], [])
    fightDict = {'main': mainActor.stats['combat ability'],
    'part1': participants[0].stats['combat ability'],
    'part2': participants[1].stats['combat ability']}
    deadNames = weightedDictRandom(fightDict, numDead)
    desc += 'and '
    deadList = []
    for theDead in deadNames:
        if theDead == 'main':
            mainActor.alive = False
            deadList.append(mainActor.name)
        elif theDead == 'part1':
            participants[0].alive = False
            deadList.append(participants[0].name)
        elif theDead == 'part2':
            participants[1].alive = False
            deadList.append(participants[1].name)
    descList = [mainActor.name, participants[0].name, participants[1].name]
    if len(deadList) == 1:
        desc += deadList[0]+' was killed!'
        descList.append(deadList[0])
    elif len(deadList) == 2:
        desc += deadList[0]+' and '+deadList[1]+'were killed!'
        descList.append(deadList[0], deadList[1])
    elif len(deadList) == 3:
        desc += ' all three died in the fighting!'
    return (desc, descList, deadList) # Second entry is the contestants named in desc, in order. Third is anyone who died. This is in strings.

Event.doEventThreeWayFight = classmethod(func)

Event.registerEvent("ThreeWayFight", Event.doEventThreeWayFight)
