import collections
import random

# This section provides special setup behavior etc. for certain class of items that cannot be added any other way
# (e.g. it needs to be factored into the Item or ItemInstance constructor). Try not to use this for behavior that could
# be incorporated in some other way.

def DossierInitialization(itemInstance, remake=False):
    if not remake and "contestant" in itemInstance.data:
        return
    chosenContestant = random.choice([v for v in itemInstance.stateStore[0]["contestants"].values() if v.alive])
    itemInstance.data["contestant"] = chosenContestant
    itemInstance.friendly += " for " + chosenContestant.name
    
ITEM_INITIALIZERS = collections.OrderedDict({
"Dossier": DossierInitialization
})

def DossierCombatChanges(itemInstance, value, otherContestant):
    if otherContestant.name == itemInstance.data["contestant"].name:
        return value + 4
    return value

ITEM_COMBAT_ABILITY_CHANGES = collections.OrderedDict({
"Dossier": DossierCombatChanges
})

# This section allows items to enforce basic restrictions on their generation, based either on the candidate it is being
# given to or (potentially) other aspects of state via stateStore.

# TODO: Some items may not be able to properly reset even if resetItemAllowed is True. Support for return False in those
# cases should be added elsewhere.

def DossierRestrictions(itemInstance, contestant, resetItemAllowed):
    if itemInstance.data["contestant"] == contestant:
        if resetItemAllowed:
            DossierInitialization(itemInstance, remake=True)
            return True
        return False
    return True

ITEM_RESTRICTIONS = collections.OrderedDict({
"Dossier": DossierRestrictions
})
