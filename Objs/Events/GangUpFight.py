
from Objs.Utilities.ArenaEnumsAndNamedTuples import EventOutput
from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    attackers = [mainActor] + participants
    desc = Event.englishList(
        attackers) + " worked together to ambush and attack " + victims[0].name + "."
    descList = attackers + victims
    fightDesc, fightDead, allKillers, lootDict, injuries, destroyedList = self.factionFight(
        attackers, victims, state["allRelationships"])
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return EventOutput(desc + fightDesc, descList, sorted([x.name for x in fightDead]), allKillers, loot_table=lootDict, injuries=injuries, destroyed_loot_table=destroyedList)


Event.registerEvent("GangUpFight", func)
