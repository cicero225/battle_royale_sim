
from ..Utilities.ArenaUtils import weightedDictRandom
from Objs.Events.Event import Event
import random
import math

TRAP_RESULT = [' fell into a spike trap set by SOURCE, impaling VICTRE on a wooden spike.', ' was struck by a hidden dart trap set by SOURCE, causing VICTIM to die slowly and painfully.', ' fell into a fall trap set by SOURCE, causing VICTIM to fall off a cliff and crack open VICTPOS skull.']
TRAP_RESULT_SELF = [' fell into SOURCE own spike trap, impaling VICTRE on a wooden spike.', ' was struck SOURCE own dart trap, causing VICTIM to die slowly and painfully.', ' fell into SOURCE own fall trap, causing VICTIM to fall off a cliff and crack open VICTPOS skull.']

def setupDiesFromTrap(state):
    state["events"]["DiesFromTrap"].eventStore["trapCounter"] = {0: 0, 1: 0, 2: 0}  # Stores existing traps
    state["events"]["DiesFromTrap"].eventStore["trapMakerCounter"] = {}  # Accounts for traps that people themselves made (to abstract away the fact that people ideally don't fall into their own traps)

Event.registerInsertedCallback("startup", setupDiesFromTrap)

# Manipulate the weight of the event based on the number of traps and who it is
def modifyTrapChance(actor, baseEventActorWeight, event):
    if event.name == "DiesFromTrap":
        thisTrapDict = event.eventStore["trapCounter"].copy()
        totSum = 0
        for key in thisTrapDict:
            if str(actor) in event.eventStore["trapMakerCounter"]:
                thisTrapDict[key] -= event.eventStore["trapMakerCounter"][str(actor)][key]
            totSum += thisTrapDict[key]
        if not totSum:
            return 0, False
        return (1 + math.log(totSum, 2))*baseEventActorWeight, True
    return baseEventActorWeight, True

Event.registerInsertedCallback("modifyIndivActorWeights", modifyTrapChance)

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    # First subtract this character's own traps from the trap list, weighted by chance of not being stupid
    notBeingStupidRatio = mainActor.stats["stability"]/10
    thisTrapDict = self.eventStore["trapCounter"].copy()
    if str(mainActor) in self.eventStore["trapMakerCounter"]:
        totSum = 0
        for key in thisTrapDict:
            thisTrapDict[key] -= self.eventStore["trapMakerCounter"][str(mainActor)][key]*notBeingStupidRatio 
            totSum += thisTrapDict[key]
        if not totSum:  # all existing traps were made by this character, cancel event
            return None
    chosen = weightedDictRandom(thisTrapDict, 1)[0]
    trapSourceDict = {key: self.eventStore["trapMakerCounter"][key][chosen] for key in self.eventStore["trapMakerCounter"]}
    if str(mainActor) in trapSourceDict:
        trapSourceDict[str(mainActor)] *= (1-notBeingStupidRatio)
    trapSource = weightedDictRandom(trapSourceDict, 1)[0]
    if trapSource == str(mainActor):
        desc = "Delirious and confused, " + str(mainActor) + TRAP_RESULT_SELF[chosen].replace("VICTIM", Event.parseGenderObject(mainActor)).replace("VICTRE", Event.parseGenderReflexive(mainActor)).replace("SOURCE", Event.parseGenderPossessive(mainActor)).replace("VICTPOS", Event.parseGenderPossessive(mainActor))
        descList = [mainActor]
    else:
        desc = str(mainActor) + TRAP_RESULT[chosen].replace("VICTIM", Event.parseGenderObject(mainActor)).replace("VICTRE", Event.parseGenderReflexive(mainActor)).replace("SOURCE", trapSource).replace("VICTPOS", Event.parseGenderPossessive(mainActor))
        descList = [mainActor, state["contestants"][trapSource]]
    
    mainActor.alive = False
    
    self.eventStore["trapCounter"][chosen] -= 1
    self.eventStore["trapMakerCounter"][trapSource][chosen] -= 1

    return (desc, descList, [str(mainActor)], {str(mainActor): trapSource})

Event.registerEvent("DiesFromTrap", func)