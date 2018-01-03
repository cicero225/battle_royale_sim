
from Objs.Events.Event import Event
import random
from collections import defaultdict


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    # they shouldn't be practicing combat if injured
    if state["callbackStore"].setdefault('InjuredDict', defaultdict(bool)):
        return None
    desc = mainActor.name + ' practiced combat'
    practiceAbility = mainActor.stats['combat ability']
    if random.random() > 1 / (1 + 1.3**practiceAbility):
        desc += ' but hurt ' + \
            Event.parseGenderReflexive(mainActor) + ' doing so.'
        mainActor.addStatus(state["statuses"]["Injury"])
    else:
        desc += ' and was successfully able to improve ' + \
            Event.parseGenderPossessive(mainActor) + ' skills'
        mainActor.permStatChange({'combat ability': 1})
    return desc, [mainActor], []


Event.registerEvent("HurtsSelfPracticingCombat", func)
