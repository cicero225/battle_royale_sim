from Objs.Events.Event import Event
from Objs.Items.Item import Item, ItemInstance

# Check that specific events that mention finding loot actually allocates all the loot to somebody.
# This is checked indirectly--if a loot table exists, which signals a fight, we just make sure all items mentioned in the description either show up somewhere in the loot table
# or are non-stackable and show up beforehand in the inventory of one doing the looting. This is unforuntately not very sensitive--if this test fails, something is wrong, but passing
# proves nothing. This is why we test with a lot of runs...
def CheckPreexistingLootAcquired(event_info, state, event_outputs):
    if event_outputs.loot_table is None or event_info["event_data"]["eventName"] not in ["FightOverItems", "FindAbandonedBuilding"]:
        return True, None
    living_pre_contestants = [event_info["pre_state"]["contestants"][x] for x in event_info["event_data"]["participants"] if state["contestants"][x].alive]
    mainActor = event_info["event_data"]["mainActor"]
    if state["contestants"][mainActor].alive:
        living_pre_contestants.append(event_info["pre_state"]["contestants"][mainActor])
    if not living_pre_contestants:  # Everyone died in this event, so loot not distributed.
        return True, None
    for potential_item in event_outputs.display_items:
        if (not isinstance(potential_item, ItemInstance) and not isinstance(potential_item, Item)) or not potential_item.lootable:
            continue
        for _, item_list in event_outputs.loot_table.items():
            for item in item_list:
                if item.is_same_item(potential_item):
                    break
            else:
                continue
            break
        else:    
            # Now check the *pre-event* inventory of survivors.
            if potential_item.stackable:
                continue
            for pre_contestant in living_pre_contestants:
                if pre_contestant.hasThing(potential_item):
                    break
            else:
                return False, "CheckPreexistingLootAcquired Failed"
    return True, None

Event.registerDebug(CheckPreexistingLootAcquired)