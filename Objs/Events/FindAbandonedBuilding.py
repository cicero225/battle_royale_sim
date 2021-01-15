from __future__ import division

from Objs.Utilities.ArenaEnumsAndNamedTuples import EventOutput
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
        lootDict = None
        destroyedList = None
        injuries = None
        if whatHappens == 0:
            desc += 'but it turned out to have nothing of value.'
            if len(eventPeople) > 1:
                probViolence = 0.25 - \
                    relationships.groupCohesion(eventPeople) / 200
                if random.random() < probViolence:
                    fightDesc, fightDead, allKillers, lootDict, injuries, destroyedList = self.fight(
                        eventPeople, relationships)
                    if fightDesc is None:
                        continue
                    desc += ' Violence broke out due to frustration.'
                    desc += fightDesc
            break
        elif whatHappens == 1:
            # get one or two random pieces of loot
            new_loot = random.sample(list(state['items'].values()), random.randint(1, 2))
            desc += ' and found sweet loot!' # let the loot be described separately
            lootDict = {}
            destroyedList = []
             # If there is no fight, there's no reason loot would be destroyed.
            overrideLootDestructionChance = 0
            if len(eventPeople) > 1:
                probViolence = 0.5 - relationships.groupCohesion(eventPeople) / 100
                if random.random() < probViolence:
                    overrideLootDestructionChange = None
                    fightDesc, fightDead, allKillers, lootDict, injuries, destroyedList = self.fight(
                        eventPeople, relationships, False, False, preexistingLoot=new_loot)
                    if fightDesc is None:
                        continue    
                    desc += ' A fight broke out over the loot.'
                    desc += fightDesc
                    break  # This has separate logic than what happens if there is no fight.
            partialLoot, partialDestroyed = self.lootForMany(eventPeople, new_loot, chanceDestroyedOverride=overrideLootDestructionChance)
            Event.MergeLootDicts(lootDict, partialLoot)
            Event.MergeDestroyedLists(destroyedList, partialDestroyed)
            break            
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
                    desc += Event.parseGenderSubject(eventPeople[0]).capitalize() + ' escaped safely.'
                     
            # This must be done separately because it assigns no killers
            # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
            return (desc, descList, [x.name for x in fightDead], collections.OrderedDict())

    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return EventOutput(desc, descList, [x.name for x in fightDead], allKillers, loot_table=lootDict, injuries=injuries, list_killers=True, destroyed_loot_table=destroyedList)


Event.registerEvent("FindAbandonedBuilding", func)
