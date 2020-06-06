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

def DossierInitialization(itemInstance, remake=False, forbidden_target=None):
    if remake or itemInstance.target is None:
        lookupList = [v for k, v in itemInstance.stateStore[0]["contestants"].items() if v.alive and (forbidden_target is None or forbidden_target.name != k)]
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
        return DossierInitialization(itemInstance, remake=True, forbidden_target=itemInstance.target)
    return True

ITEM_RESTRICTIONS = collections.OrderedDict({
"Dossier": DossierRestrictions
})

def LoveOnAcquisition(itemInstance, contestant, state):
    itemInstance.eventHandlers.pop("Love", None)
    from Objs.Sponsors.Sponsor import Sponsor
    if isinstance(contestant, Sponsor):
        return
    from Objs.Events.IndividualEventHandler import IndividualEventHandler
    from Objs.Contestants.Contestant import Contestant
    newHandler = IndividualEventHandler(state)  
    if isinstance(itemInstance.target, Sponsor):
        newHandler.banEventForSingleContestant("ShareIntimateConversation", str(contestant))
        # This is done manually, but should be systematized if this becomes a common need.
        def func(contestantKey, thisevent, state, participants, victims, sponsorsHere, alreadyUsed):
            if thisevent.name in ["SponsorCheatKill", "MadokamiKillsBadWorshipper", "HomuciferKillsBadWorshipper"] and contestantKey == str(contestant) and str(sponsorsHere[0]) == str(itemInstance.target):
                return False, True
            if thisevent.name == "ShareIntimateConversation"  and str(participants[0]) == str(contestant):
                return False, True
            return True, False

        def anonfunc(contestantKey, thisevent, state, participants, victims, sponsorsHere, alreadyUsed): return func(contestantKey, thisevent,
                                                                                                        state, participants, victims, sponsorsHere, alreadyUsed)  # this anonymizes func, giving a new reference each time this is called
        newHandler.registerEvent("overrideContestantEvent", anonfunc)
    else:
        newHandler.banMurderEventsAtoB(str(contestant), itemInstance.target, ["FightOverItems", "FindAbandonedBuilding"])
        newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "ShareStoryofLife", True)
        newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "ShareIntimateConversation", True)
        newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "FriendGivesMedicine", True)
        newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "FriendHelpsInjury", True)
        newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "AWorshipsB", True)
        newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "GangUpFight", True)
        newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "ACooksForB", True)
        newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "FightOverItems", True)
        newHandler.bindRoleForContestantAndEvent("participants", contestant, itemInstance.target, "FindAbandonedBuilding", True)

    itemInstance.eventHandlers["Love"] = newHandler
   
def DossierOnAcquisition(itemInstance, contestant, state):
    if itemInstance.target == contestant:
        from Objs.Events.Event import Event  # Again, this should really be in Arenautils...
        # Destroy self-dossiers.
        state["announcementQueue"].append((contestant.name + " destroyed a dossier about " + Event.parseGenderReflexive(contestant) + ".",
                                          [contestant, itemInstance], state, {}))
        contestant.removeItem(itemInstance, itemInstance.count)

ITEM_ON_ACQUISITION = collections.OrderedDict({
"Love": LoveOnAcquisition,
"Dossier": DossierOnAcquisition
})

def LoveOnRemoval(itemInstance, contestant, state):
    itemInstance.eventHandlers.pop("Love", None)

ITEM_ON_REMOVAL = collections.OrderedDict({
"Love": LoveOnRemoval
})

# For these display rules, returning None implies standard processing. Returning "" implies nothing.
def DossierDisplayRule(itemInstance, contestant, state):
    # Don't display dossiers for dead people (though we keep them around in case of resurrection.)
    if itemInstance.target is None or itemInstance.target.alive:
        return None
    return ""

ITEM_DISPLAY_OVERRIDE = collections.OrderedDict({
"Dossier": DossierDisplayRule
})

def DossierImageDisplayRule(itemInstance, contestant, state):
    # Don't display dossiers for dead people (though we keep them around in case of resurrection.)
    if itemInstance.target is None or itemInstance.target.alive:
        return None
    return ""

ITEM_IMAGE_DISPLAY_OVERRIDE = collections.OrderedDict({
"Dossier": DossierImageDisplayRule
})

# This section allows items to accept extra arguments (as a dict) at creation time. Note that this must be explicitly provided in the
# code - if an item may be made arbitrarily, it cannot strictly depend on this being called to function.

ITEM_EXTRA_ARGUMENTS = collections.OrderedDict({})