
from Objs.Events.Event import Event, EventOutput
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = CLIFF_DESCRIPTIONS[random.randint(0, len(CLIFF_DESCRIPTIONS) - 1)](mainActor, victims[0])
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -4)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -6)
    victims[0].kill()
    if mainActor.stats["stability"] < 3:
        desc += ' ' + Event.parseGenderSubject(mainActor).capitalize() + ' smiled as ' + Event.parseGenderSubject(
            mainActor) + ' watched ' + Event.parseGenderObject(victims[0]) + ' die.'
        mainActor.permStatChange({'stability': -1})
    tempList = [mainActor, victims[0]]
    lootDict = Event.lootAll(mainActor, victims[0])
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return EventOutput(desc, tempList, [victims[0].name], loot_table=lootDict)

CLIFF_DESCRIPTIONS = [
    lambda mainActor, victim : mainActor.name + ' invited ' + str(victim) + ' up to the top of a gorge to admire the view, but betrayed ' + Event.parseGenderObject(
        victim) + ', pushing ' + Event.parseGenderObject(victim) + ' off the cliff to ' + Event.parseGenderPossessive(victim) + ' death.',
    lambda mainActor, victim : mainActor.name + ' invited ' + str(victim) + ' to spar together, but betrayed ' + Event.parseGenderObject(
        victim) + ', stabbing them during an opportune moment in the fight.',
    lambda mainActor, victim : mainActor.name + ' offered to watch ' + str(victim) + "'s back while sneaking up on a clearing, then betrayed " + Event.parseGenderObject(
        victim) + ', stabbing ' + Event.parseGenderObject(victim) + ' in the back.'      
]

Event.registerEvent("BetrayFriendGuaranteedDeath", func)
