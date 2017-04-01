
from Objs.Events.Event import Event
import random

TRAPS = ['spike trap', 'poison dart trap', 'fall trap']

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    trap_type = random.randint(0,2)
    desc = str(mainActor) + ' built a deadly ' + TRAPS[trap_type] + ' to kill other contestants with.'
    
    state["events"]["DiesFromTrap"].eventStore["trapCounter"][trap_type] += 1
    state["events"]["DiesFromTrap"].eventStore["trapMakerCounter"].setdefault(str(mainActor), {0: 0, 1: 0, 2: 0}) 
    state["events"]["DiesFromTrap"].eventStore["trapMakerCounter"][str(mainActor)][trap_type] += 1

    return (desc, [mainActor], [])

Event.registerEvent("SetTrap", func)
