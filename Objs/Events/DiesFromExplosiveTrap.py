
from ..Utilities.ArenaUtils import weightedDictRandom, DictToOrderedDict
from Objs.Events.Event import Event
import collections
import random
import math

def setupDiesFromExplosiveTrap(state):
    state["events"]["DiesFromExplosiveTrap"].eventStore.setdefault("trapCounter", 0)
    state["events"]["DiesFromExplosiveTrap"].eventStore.setdefault("trapMakerCounter", collections.OrderedDict())

Event.registerInsertedCallback("startup", setupDiesFromExplosiveTrap)


# Manipulate the weight of the event based on the number of traps and who it is

def modifyExplosiveTrapChance(actor, baseEventActorWeight, event):
    if event.name == "DiesFromExplosiveTrap":
        trapCounter = event.eventStore["trapCounter"]
        if trapCounter == 0:
            return 0, False
        return (1 + math.log(trapCounter, 2)) * baseEventActorWeight, True
    return baseEventActorWeight, True


Event.registerInsertedCallback("modifyIndivActorWeights", modifyExplosiveTrapChance)

# It's really complicated to emulate people not falling into their own traps with multiple participants, etc., so we'll take a different tack here than in the other traps.

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):    
    if self.eventStore["trapCounter"] == 0:
        return None
    everyone = [mainActor] + participants
    # First determine who this trap belongs to.
    trapSource = weightedDictRandom(self.eventStore["trapMakerCounter"])[0]
    desc = Event.englishList(everyone) + " stumbled into an explosive trap set by " + trapSource + ", "   
    # If the maker of this trap is anywhere in the group, chance that they warn the group.
    found = False
    for person in everyone:
        if str(person) == trapSource:
            found = True
            notBeingStupidRatio = (mainActor.stats["stability"] + mainActor.stats["cleverness"]*3) / 40
            if random.random() < notBeingStupidRatio:
                if len(everyone) > 1:
                    desc += " but they were able to escape thanks to " + str(person) + "'s warning!"
                else:
                    desc += " but excaped from " + Event.parseGenderPossessive(mainActor) + " own trap."
                return (desc, everyone, [])
        break
    desc += " and they all died in the ensuing detonation!" if (len(everyone) > 1) else " and " + Event.parseGenderSubject(mainActor) + " died in the ensuing detonation!"
    for person in everyone:
        person.alive = False
    self.eventStore["trapCounter"] -= 1
    self.eventStore["trapMakerCounter"][trapSource] -= 1
    descList = [mainActor] + participants
    if not found:
        descList.append(state["contestants"][trapSource])
    return (desc, descList, [str(x) for x in everyone], {str(x): trapSource for x in everyone}, everyone)

Event.registerEvent("DiesFromExplosiveTrap", func)
