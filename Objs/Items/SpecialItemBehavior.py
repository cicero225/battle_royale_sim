import collections
import random

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
ITEM_INITIALIZERS = collections.OrderedDict({
"Dossier": DossierInitialization
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

# This section allows items to accept extra arguments (as a dict) at creation time. Note that this must be explicitly provided in the
# code - if an item may be made arbitrarily, it cannot strictly depend on this being called to function.

ITEM_EXTRA_ARGUMENTS = collections.OrderedDict({})