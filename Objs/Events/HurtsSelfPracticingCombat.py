
from Objs.Events.Event import Event
import random
from collections import defaultdict

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    state["callbackStore"].setdefault('InjuredDict',defaultdict(bool))
    if state["callbackStore"]['InjuredDict'][mainActor.name]:  # they shouldn't be practicing combat if injured
        return None
    desc = mainActor.name+' practiced combat'
    practiceAbility = mainActor.stats['combat ability']
    if random.random()> 1/(1+1.3**practiceAbility):
        desc += ' but hurt '+Event.parseGenderReflexive(mainActor)+' doing so.'
        mainActor.SetInjured()
    else:
        desc += ' and was successfully able to improve '+Event.parseGenderPossessive(mainActor)+' skills'
        mainActor.permStatChange({'combat ability': 1})
    return desc, [mainActor], []

Event.registerEvent("HurtsSelfPracticingCombat", func)