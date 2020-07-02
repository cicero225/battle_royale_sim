from Objs.Items.Item import Item
from Objs.Events.Event import Event
import collections
import random


def spreadDisease(thisWriter, eventOutputs, thisEvent, state):
    # This happens fairly often, so might as well shortcut this
    if len(eventOutputs[1]) < 2:
        return
    no_contact = [] if eventOutputs.no_contact is None else [str(x) for x in eventOutputs.no_contact]
    for disease, disease_item in state["statuses"].items():
        disease_stats = disease_item.rawData.get("contagious")
        if disease_stats is None:
            continue
        chanceSpread = disease_stats["ChanceSpread"]
        requiresContact = disease_stats["RequiresContact"]
        if requiresContact and not thisEvent.baseProps.get("contact", False):
            continue
        # descContestants, a more reliable guide to who was involved than eventOutputs[4], even if it exists, because we care about everyone involved
        potentialContestants = [
            x for x in eventOutputs[1] if str(x) in state["contestants"] and str(x) not in no_contact]
        # note some people here will be dead, but are still valid disease vectors (but shouldn't _catch_ a disease)
        hasDisease = [x for x in potentialContestants if x.hasThing(disease)]
        if not hasDisease:
            return
        # Each person who already has the disease has a chance to spread it to every other person. I will pull it from the instance, in case in the future we have diseases with changing spread chances.
        for contestant in sorted(list(set(potentialContestants) - set(hasDisease)), key=lambda x: str(x)):
            if not contestant.alive:
                continue
            # Chance procs for each person already sick
            for sickPerson in hasDisease:
                if random.random() < chanceSpread:
                    contestant.addStatus(disease)
                    output_str = str(contestant) + " caught " + state["statuses"][disease].friendly + " from " + str(sickPerson)
                    if thisWriter is None:
                        print(output_str)
                        break
                    thisWriter.addEvent(str(contestant) + " caught " + state["statuses"][disease].friendly + " from " + str(
                        sickPerson), [contestant, state["statuses"][disease], sickPerson])
                    break


Item.registerInsertedCallback("postEventWriterCallbacks", spreadDisease)


# manages the Medkit Evening Healing

def medkitHealing(thisPhase, printHTML, state):
    if thisPhase != "Evening":
        return
    for contestant in state["contestants"].values():
        if contestant.alive and contestant.hasThing("Medical Kit"):
            removedStatuses = set()
            if contestant.removeStatus("Injury"):  # If this is False, they never had it to start with.
                removedStatuses.add(state["statuses"]["Injury"])
            if contestant.removeStatus("Fever"):  # If this is False, they never had it to start with.
                removedStatuses.add(state["statuses"]["Fever"])
            if removedStatuses and printHTML:
                desc = contestant.name + " used their Medical Kit to heal their " + Event.englishList(removedStatuses) + "."
                descContestants = [contestant, *removedStatuses]
                state['thisWriter'].addEvent(desc, descContestants)
            
Item.registerPostPhaseCallback(medkitHealing)