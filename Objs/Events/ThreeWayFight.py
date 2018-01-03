
from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = mainActor.name + ', ' + \
        participants[0].name + ', and ' + participants[1].name + ' fought, '
    descList = [mainActor, participants[0], participants[1]]
    fightDesc, fightList, fightDead, allKillers = Event.fight(
        descList, state['allRelationships'], state['settings'])
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc + fightDesc, descList + fightList, [x.name for x in fightDead], allKillers)


Event.registerEvent("ThreeWayFight", func)
