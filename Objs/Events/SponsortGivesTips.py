from Objs.Events.Event import Event
from Objs.Events.IndividualEventHandler import IndividualEventHandler
import random

def checkSponsorLove(actor, sponsor, baseEventActorWeight, event):
    if event.name != "SponsorGivesTips":
        return baseEventActorWeight, True
    possible_love = actor.hasThing("Love")
    if not possible_love or str(possible_love[0].target) != str(sponsor):    
        return baseEventActorWeight, True
    return baseEventActorWeight*event.stateStore[0]["settings"]["relationInfluence"], True

Event.registerInsertedCallback(
    "modifyIndivActorWeightsWithSponsors", checkSponsorLove)

def checkActorLove(actor, origWeight, event):
    if event.name == "SponsorGivesTips" and actor.hasThing("Love"):
        return (origWeight*event.stateStore[0]["settings"]["relationInfluence"]/3, True)

Event.registerEvent("modifyIndivActorWeights", checkActorLove)

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    state["allRelationships"].IncreaseFriendLevel(
        mainActor, sponsors[0], random.randint(2, 3))
    mainActor.permStatChange({'survivalism': 2,
                              'cleverness': 2})
    choice = random.randint(0, 1)

    # This cannot happen more than once
    eventHandler = IndividualEventHandler(state)
    eventHandler.banEventForSingleContestant(
        "SponsorGivesTips", mainActor.name)
    # This will remain in place for the rest of the game
    self.eventStore[mainActor.name] = eventHandler
    potential_love = sponsors[0].hasThing("Love")
    if choice or (potential_love and str(potential_love[0].target) == str(mainActor)):
        desc = sponsors[0].name + \
            ' gave a map and a book of instructions to ' + mainActor.name + "."
        return (desc, [sponsors[0], mainActor], [])
    else:
        desc = 'An unknown sponsor gave a map and a book of instructions to ' + \
            mainActor.name + "."
        # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
        return (desc, [mainActor], [])


Event.registerEvent("SponsorGivesTips", func)
