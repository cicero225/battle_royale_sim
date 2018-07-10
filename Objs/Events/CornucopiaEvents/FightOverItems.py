from __future__ import division

from Objs.Events.Event import Event
from ...Utilities.ArenaUtils import weightedDictRandom
import collections
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    
    eventPeople = [mainActor] + participants
    numItems = random.randint(1, 2)
    itemsFound = random.sample(list(state['items'].values()), 2)
    descList = eventPeople + itemsFound
    Event.lootRandom(eventPeople, itemsFound)
    fightDesc, fightList, fightDead, allKillers = Event.fight(
        eventPeople, state["allRelationships"], state['settings'])
    desc = Event.englishList(eventPeople) + " stumbled across " + Event.englishList(itemsFound) + " at the same time. A fight broke out, " + fightDesc
    descList += fightList
    
    return (desc, descList, [x.name for x in fightDead], allKillers)


Event.registerEvent("FightOverItems", func)