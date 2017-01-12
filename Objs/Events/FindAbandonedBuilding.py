from __future__ import division

from Objs.Events.Event import Event
from ..Utilities.ArenaUtils import weightedDictRandom
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    whatHappens = random.randint(0,2) # 0 is empty, 1 is loot, 2 is trap
    eventPeople = [mainActor]+participants
    descList = eventPeople.copy()
    desc = Event.englishList(eventPeople)+' found an abandoned building, '
    relationships = state["allRelationships"]
    fightDead = []
    if whatHappens == 0:
        desc += 'but it turned out to have nothing of value.'
        if len(eventPeople)>1:
            probViolence = 0.25-relationships.groupCohesion(eventPeople)/200
            if random.random()<probViolence:
                desc += ' Violence broke out due to frustration, and '
                fightDesc, fightList, fightDead = Event.fight(eventPeople, relationships, state['settings'])
                desc += fightDesc
                descList += fightList
    elif whatHappens == 1:
        numItems = random.randint(1,2)
        itemsFound = random.sample(list(state['items'].values()), 2)
        desc += ' and found '+Event.englishList(itemsFound)+'.' 
        descList += itemsFound
        Event.lootRandom(eventPeople, itemsFound)
        if len(eventPeople)>1:    
            probViolence = 0.5-relationships.groupCohesion(eventPeople)/100
            if random.random()<probViolence:
                desc += ' A fight broke out over the loot, '
                fightDesc, fightList, fightDead = Event.fight(eventPeople, relationships, state['settings'])
                desc += fightDesc
                descList += fightList
    elif whatHappens == 2:
        desc += ' but the building was booby-trapped! '
        for person in eventPeople:
            if person.stats['cleverness']+person.stats['combat ability']+random.randint(0, 21)<21:
                person.alive = False
                fightDead.append(person)
        if not fightDead:
            if len(eventPeople)>1:
                desc += 'Everyone escaped safely.'
            else:
                desc += Event.parseGenderSubject(eventPeople[0])+' escaped safely.'
        elif len(fightDead) == 1:
            desc += Event.englishList(fightDead)+' was killed.'
        else:
            desc += Event.englishList(fightDead)+' were killed.'    
    
    return (desc, descList, [x.name for x in fightDead]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventFindAbandonedBuilding = classmethod(func)

Event.registerEvent("FindAbandonedBuilding", Event.doEventFindAbandonedBuilding)
