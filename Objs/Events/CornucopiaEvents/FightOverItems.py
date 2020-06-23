from __future__ import division

from Objs.Events.Event import Event, EventOutput
from Objs.Items.Item import ItemInstance
from ...Utilities.ArenaUtils import weightedDictRandom
import collections
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    
    eventPeople = [mainActor] + participants
    numItems = random.randint(1, 2)
    itemsFound = [ItemInstance.takeOrMakeInstance(v) for v in random.sample(list(state['items'].values()), 2)]
    descList = eventPeople + itemsFound
    # We deliberately don't record the output here, because we're about to redestribute the loot again.
    # todo: this doesn't work properly, because if no one dies, we never get a message about who got the original loot
    Event.lootRandom(eventPeople, itemsFound)
    fightDesc, fightDead, allKillers, lootDict, injuries = Event.fight(
        eventPeople, state["allRelationships"], state['settings'])
    if fightDesc is None:
        return None
    desc = Event.englishList(eventPeople) + " stumbled across " + Event.englishList(itemsFound) + " at the same time. A fight broke out. " + fightDesc
    
    return EventOutput(desc, descList, [x.name for x in fightDead], allKillers, loot_table=lootDict, injuries=injuries, list_killers=True)


Event.registerEvent("FightOverItems", func)
