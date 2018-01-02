
from ..Utilities.ArenaUtils import weightedDictRandom, DictToOrderedDict
from Objs.Events.Event import Event
from Objs.Events.IndividualEventHandler import IndividualEventHandler
import collections
import random

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    # Unlike other events, this doesn't "consume" the other participant, but it does need to pick one.
    # Weight chance of contestant being chosen by friendship and love level.
    potentialContestants = DictToOrderedDict({x.name:(abs(state["allRelationships"].friendships[mainActor.name][x.name])+2*abs(state["allRelationships"].loveships[mainActor.name][x.name])) for x in state["contestants"].values() if x.alive and x != mainActor})
    if not potentialContestants:
        return None
    #Rig the rate for Homura and Madoka
    if "Akemi Homura" in potentialContestants:
        potentialContestants["Akemi Homura"] *=10
    if "Kaname Madoka" in potentialContestants:
        potentialContestants["Kaname Madoka"] *=10
    chosen = weightedDictRandom(potentialContestants, 1)[0]
    state["allRelationships"].IncreaseFriendLevel(mainActor, state["contestants"][chosen], 10)
    state["allRelationships"].IncreaseLoveLevel(mainActor, state["contestants"][chosen], 10)
    mainActor.permStatChange({'stability': 2})
    eventHandler = IndividualEventHandler(state)
    eventHandler.banMurderEventsAtoB(mainActor.name, chosen)
    eventHandler.banEventForSingleContestant("AWorshipsB", mainActor.name, state)
    self.eventStore.setdefault("permanent", collections.OrderedDict())[mainActor.name] = eventHandler
    if chosen == "Kaname Madoka":
        eventHandler = IndividualEventHandler(state)
        eventHandler.setEventWeightForSingleContestant("HomuciferKillsBadWorshipper", mainActor.name, 10, state)
        state["allRelationships"].IncreaseFriendLevel(state["sponsors"]["Madokami"], mainActor, 10)
        self.eventStore[mainActor.name] = eventHandler
    elif chosen == "Akemi Homura":
        eventHandler = IndividualEventHandler(state)
        eventHandler.setEventWeightForSingleContestant("MadokamiKillsBadWorshipper", mainActor.name, 10, state)
        state["allRelationships"].IncreaseFriendLevel(state["sponsors"]["Akuma Homura"], mainActor, 10)
        self.eventStore[mainActor.name] = eventHandler
    desc = 'In a delirious state, '+mainActor.name+' had a religious epiphany, realizing that '+chosen+' is the avatar of a divine being.'
    return (desc, [mainActor, state["contestants"][chosen]], [])

Event.registerEvent("AWorshipsB", func)
