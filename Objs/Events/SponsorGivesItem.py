from Objs.Events.Event import Event
import random


def checkSponsorLove(actor, sponsor, baseEventActorWeight, event):
    if event.name != "SponsorGivesItem":
        return baseEventActorWeight, True
    possible_love = actor.hasThing("Love")
    if not possible_love or str(possible_love[0].target) != str(sponsor):    
        return baseEventActorWeight, True
    return baseEventActorWeight*event.stateStore[0]["settings"]["relationInfluence"], True

Event.registerInsertedCallback(
    "modifyIndivActorWeightsWithSponsors", checkSponsorLove)

def checkActorLove(actor, origWeight, event):
    if event.name == "SponsorGivesItem" and actor.hasThing("Love"):
        return (origWeight*event.stateStore[0]["settings"]["relationInfluence"]/3, True)

Event.registerEvent("modifyIndivActorWeights", checkActorLove)

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    options = sorted(set(str(x) for x in state["items"].values(
    )) - set(str(x) for x in mainActor.inventory if not x.stackable), key=lambda x: str(x))
    if not options:
        return None  # Pick a different event
    itemInstance = None
    while itemInstance is None:
        gift = random.choice(options)
        itemInstance = mainActor.addItem(gift, isNew=True, resetItemAllowed=True)
    assert(itemInstance.target != mainActor)  # Sentinal for a bug we were having for a long while. If this doesn't trigger for a long while, this can be deleted.
    # To get the actual item name, we need to get the name of the item INSTANCE
    friendlyName = itemInstance.friendly
    state["allRelationships"].IncreaseFriendLevel(
        mainActor, sponsors[0], random.randint(1, 2))
    potential_love = sponsors[0].hasThing("Love")
    if random.random() < 0.8 or (potential_love and str(potential_love[0].target) == str(mainActor)):
        desc = sponsors[0].name + ' gave ' + \
            friendlyName + ' to ' + mainActor.name + "."
        return (desc, [sponsors[0], itemInstance, mainActor], [])
    else:
        desc = 'An unknown sponsor gave ' + friendlyName + ' to ' + mainActor.name + "."
        # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
        return (desc, [itemInstance, mainActor], [])


Event.registerEvent("SponsorGivesItem", func)
