
from Objs.Events.Event import Event, EventOutput
import random
from collections import defaultdict


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    # they shouldn't be practicing combat if injured
    if state["callbackStore"].setdefault('InjuredDict', defaultdict(bool)):
        return None
    desc = mainActor.name + ' practiced combat'
    practiceAbility = mainActor.stats['combat ability']
    injuries = None
    if random.random() > 1 / (1 + 1.3**practiceAbility):
        desc += ' but hurt ' + \
            Event.parseGenderReflexive(mainActor) + ' doing so.'
        mainActor.addStatus(state["statuses"]["Injury"])
        injuries.append(str(mainActor))
    else:
        desc += ' and was successfully able to improve ' + \
            Event.parseGenderPossessive(mainActor) + ' skills'
        mainActor.permStatChange({'combat ability': 1})
    return EventOutput(desc, [mainActor], [], injuries=injuries)


Event.registerEvent("HurtsSelfPracticingCombat", func)
