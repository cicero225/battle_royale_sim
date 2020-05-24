from __future__ import division

from Objs.Events.Event import Event
from ..Utilities.ArenaUtils import weightedDictRandom
import collections
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    eventPeople = [mainActor] + participants
    relationships = state["allRelationships"]
    while True:
        whatHappens = random.randint(0, 2)  # 0 is empty, 1 is loot, 2 is trap  
        descList = eventPeople.copy()
        desc = Event.englishList(eventPeople) + ' found an abandoned building, '
        fightDead = []
        allKillers = None
        if whatHappens == 0:
            desc += 'but it turned out to have nothing of value.'
            if len(eventPeople) > 1:
                probViolence = 0.25 - \
                    relationships.groupCohesion(eventPeople) / 200
                if random.random() < probViolence:
                    fightDesc, fightList, fightDead, allKillers = Event.fight(
                        eventPeople, relationships, state['settings'])
                    if fightDesc is None:
                        continue
                    desc += ' Violence broke out due to frustration.'
                    desc += fightDesc
                    descList += fightList
        elif whatHappens == 1:
            numItems = random.randint(1, 2)
            itemsFound = Event.lootRandom(eventPeople, random.sample(list(state['items'].values()), 2))
            desc += ' and found ' + Event.englishList(itemsFound) + '.'
            descList += itemsFound
            if len(eventPeople) > 1:
                probViolence = 0.5 - relationships.groupCohesion(eventPeople) / 100
                if random.random() < probViolence:
                    fightDesc, fightList, fightDead, allKillers = Event.fight(
                        eventPeople, relationships, state['settings'])
                    if fightDesc is None:
                        continue    
                    desc += ' A fight broke out over the loot.'
                    desc += fightDesc
                    descList += fightList
        elif whatHappens == 2:
            desc += ' but the building was booby-trapped! '
            for person in eventPeople:
                if person.stats['cleverness'] + person.stats['combat ability'] + random.randint(0, 21) < 21:
                    person.kill()
                    fightDead.append(person)
            if not fightDead:
                if len(eventPeople) > 1:
                    desc += 'Everyone escaped safely.'
                else:
                    desc += Event.parseGenderSubject(
                        eventPeople[0]) + ' escaped safely.'
            else:
                desc += '\n\nKilled: ' + Event.englishList(fightDead)
            # This must be done separately because it assigns no killers
            # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
            return (desc, descList, [x.name for x in fightDead], collections.OrderedDict())

        # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
        return (desc, descList, [x.name for x in fightDead], allKillers)


Event.registerEvent("FindAbandonedBuilding", func)
