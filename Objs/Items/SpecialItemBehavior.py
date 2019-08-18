import collections
import random

# This will be placed into game startup and enables arbitrary item-related modifications.
def LoveGlobalDeathRule(state):
    from Objs.Events.Event import Event
    def BreakHeartForDead(contestant, state):
        potential_love = contestant.hasThing("Love")
        if not potential_love:
            return
        lover = potential_love[0].target
        # if lover is also dead, return immediately.
        if not lover.alive:
            return
        new_lover = state["allRelationships"].SetNewRomance(lover)
        if new_lover is None:
            Event.announce(str(lover) + " was heartbroken by the death of " + str(contestant), [lover, state["statuses"]["LoveBroken"]])
        else:
            Event.announce("Because of " + str(contestant) + "'s death, " + str(lover) + " is now in a romance with " + str(new_lover), [lover, state["statuses"]["Love"], new_lover])       
    from Objs.Contestants.Contestant import Contestant
    Contestant.onDeathCallbacks.append(BreakHeartForDead)

PRE_GAME_ITEM_RULES = [LoveGlobalDeathRule]

# This section provides special setup behavior etc. for certain class of items that cannot be added any other way
# (e.g. it needs to be factored into the Item or ItemInstance constructor). Try not to use this for behavior that could
# be incorporated in some other way.

def DossierInitialization(itemInstance, remake=False):
    if itemInstance.target is None:
        lookupList = [v for k, v in itemInstance.stateStore[0]["contestants"].items() if v.alive and (itemInstance.target is None or itemInstance.target.name != k)]
        if not lookupList:  # edge case, only one person is still alive.
            return False
        itemInstance.target = random.choice(lookupList) 
    itemInstance.friendly = itemInstance.item.friendly + " for " + itemInstance.target.name
    return True
  
def LoveInitialization(itemInstance, remake=False):
    itemInstance.friendly = itemInstance.item.friendly + " for " + itemInstance.target.name
    return True
  
ITEM_INITIALIZERS = collections.OrderedDict({
"Dossier": DossierInitialization,
"Love": LoveInitialization
})

def DossierCombatChanges(itemInstance, value, thisContestant, otherContestant):
    if (otherContestant.name == itemInstance.target.name) or (thisContestant.name == itemInstance.target.name) :
        return value + 4
    return value

ITEM_COMBAT_ABILITY_CHANGES = collections.OrderedDict({
"Dossier": DossierCombatChanges
})

# This section allows items to enforce basic restrictions on their generation, based either on the candidate it is being
# given to or (potentially) other aspects of state via stateStore.

# TODO: Some items may not be able to properly reset even if resetItemAllowed is True. Support for return False in those
# cases should be added elsewhere.

def DossierRestrictions(itemInstance, contestant, isNew, resetItemAllowed):
    if isNew and itemInstance.target == contestant and not resetItemAllowed:
        return False
    if itemInstance.target == contestant and resetItemAllowed:
        return DossierInitialization(itemInstance, remake=True)
    return True

ITEM_RESTRICTIONS = collections.OrderedDict({
"Dossier": DossierRestrictions
})

def LoveOnAcquisition(itemInstance, contestant, state):
    itemInstance.eventHandlers.pop("Love", None)
    from Objs.Sponsors.Sponsor import Sponsor
    if isinstance(contestant, Sponsor) or isinstance(itemInstance.target, Sponsor):
        return
    from Objs.Events.IndividualEventHandler import IndividualEventHandler
    newHandler = IndividualEventHandler(state)
    newHandler.banMurderEventsAtoB(str(contestant), itemInstance.target)
    newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "ShareStoryofLife", True)
    newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "ShareIntimateConversation", True)
    newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "FriendGivesMedicine", True)
    newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "AWorshipsB", True)
    newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "FriendHelpsInjury", True)
    newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "GangUpFight", True)
    newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "ACooksForB", True)
    itemInstance.eventHandlers["Love"] = newHandler

ITEM_ON_ACQUISITION = collections.OrderedDict({
"Love": LoveOnAcquisition
})

def LoveOnRemoval(itemInstance, contestant, state):
    itemInstance.eventHandlers.pop("Love", None)

ITEM_ON_REMOVAL = collections.OrderedDict({
"Love": LoveOnRemoval
})


# This section allows items to accept extra arguments (as a dict) at creation time. Note that this must be explicitly provided in the
# code - if an item may be made arbitrarily, it cannot strictly depend on this being called to function.

ITEM_EXTRA_ARGUMENTS = collections.OrderedDict({})