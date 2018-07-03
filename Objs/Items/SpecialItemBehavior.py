import collections
import random

# This file provides special setup behavior etc. for certain class of items that cannot be added any other way
# (e.g. it needs to be factored into the Item or ItemInstance constructor). Try not to use this for behavior that could
# be incorporated in some other way.

def DossierInitialization(itemInstance):
    if "contestant" in itemInstance.data:
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