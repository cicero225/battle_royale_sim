from Objs.Events.Event import Event
from collections import defaultdict

def countDaysWithoutWater(state):
    for contestant in state["contestants"].values():
        if state["items"]["Clean Water"] in contestant.inventory:
            state["events"]["Dysentary"].eventStore["daysWithoutWater"][str(contestant)] = 0
        else:
            state["events"]["Dysentary"].eventStore["daysWithoutWater"][str(contestant)] += 1

Event.registerInsertedCallback("postDayCallbacks", countDaysWithoutWater)

def adjustDysenteryChance(actor, indivProb, event):
    if str(event) == "Dysentary":
        event.eventStore.setdefault("daysWithoutWater", defaultdict(int))  # initializes if not present, by default it always returns 0
        indivProb *= event.eventStore["daysWithoutWater"][str(actor)]  # A simple linear multiplier, more merciful and easier than exponential
    return indivProb, True

Event.registerInsertedCallback("modifyIndivActorWeights", adjustDysenteryChance)

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.alive = False
    desc = mainActor.name + " died horribly of dysentery."
    return (desc, [mainActor], [mainActor.name]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("Dysentary", func)
