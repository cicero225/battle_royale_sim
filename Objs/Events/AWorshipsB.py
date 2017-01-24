
from ..Utilities.ArenaUtils import weightedDictRandom
from Objs.Events.Event import Event
from Objs.Events.IndividualEventHandler import IndividualEventHandler
import random

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    # Unlike other events, this doesn't "consume" the other participant, but it does need to pick one.
    # Weight chance of contestant being chosen by friendship and love level.
    potentialContestants = {x.name:(abs(state["allRelationships"].friendships[mainActor.name][x.name])+2*abs(state["allRelationships"].loveships[mainActor.name][x.name])) for x in state["contestants"].values() if x.alive and x != mainActor}
    #Rig the rate for Homura and Madoka
    if "Akemi Homura" in potentialContestants:
        potentialContestants["Akemi Homura"] *=10
    if "Kaname Madoka" in potentialContestants:
        potentialContestants["Kaname Madoka"] *=10
    print(potentialContestants)
    chosen = weightedDictRandom(potentialContestants, 1)[0]
    state["allRelationships"].IncreaseFriendLevel(mainActor, state["contestants"][chosen], 10)
    state["allRelationships"].IncreaseLoveLevel(mainActor, state["contestants"][chosen], 10)
    mainActor.permStatChange({'stability': 2})
    eventHandler = IndividualEventHandler(state)
    eventHandler.banMurderEventsAtoB(mainActor.name, chosen)
    eventHandler.banEventForSingleContestant("AWorshipsB", mainActor.name)
    self.eventStore[mainActor.name] = eventHandler
    desc = 'In a delirious state, '+mainActor.name+' had a religious epiphany, realizing that '+chosen+' is the avatar of a divine being.'
    return (desc, [mainActor], [])

Event.registerEvent("AWorshipsB", func)
