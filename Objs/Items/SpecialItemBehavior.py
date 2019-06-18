import collections
import random

# This section provides special setup behavior etc. for certain class of items that cannot be added any other way
# (e.g. it needs to be factored into the Item or ItemInstance constructor). Try not to use this for behavior that could
# be incorporated in some other way.

def DossierInitialization(itemInstance, remake=False):
    if not remake and "contestant" in itemInstance.data:
        return True
    lookupList = [v for k, v in itemInstance.stateStore[0]["contestants"].items() if v.alive and ("contestant" not in itemInstance.data or itemInstance.data["contestant"].name != k)]
    if not lookupList:  # edge case, only one person is still alive.
        return False
    chosenContestant = random.choice(lookupList)
    itemInstance.data.clear()
    itemInstance.data["contestant"] = chosenContestant
    itemInstance.friendly = itemInstance.item.friendly + " for " + chosenContestant.name
    return True
    
ITEM_INITIALIZERS = collections.OrderedDict({
"Dossier": DossierInitialization
})

def DossierCombatChanges(itemInstance, value, thisContestant, otherContestant):
    if (otherContestant.name == itemInstance.data["contestant"].name) or (thisContestant.name == itemInstance.data["contestant"].name) :
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
    if isNew and itemInstance.data["contestant"] == contestant and not resetItemAllowed:
        return False
    if itemInstance.data["contestant"] == contestant and resetItemAllowed:
        return DossierInitialization(itemInstance, remake=True)
    return True

ITEM_RESTRICTIONS = collections.OrderedDict({
"Dossier": DossierRestrictions
})
