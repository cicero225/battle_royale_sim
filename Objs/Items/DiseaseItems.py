from Objs.Items.Item import Item
import collections
import random

# The numbers here are the chance the disease spreads per interaction per person.
DISEASE_ITEMS = collections.OrderedDict()
DISEASE_ITEMS["Fever"] = 0.5

def spreadDisease(thisWriter, eventOutputs, state):
    if len(eventOutputs[1]) < 2:  # This happens fairly often, so might as well shortcut this
        return
    for disease in DISEASE_ITEMS:
        potentialContestants = [x for x in eventOutputs[1] if str(x) in state["contestants"]]  # descContestants, a more reliable guide to who was involved than eventOutputs[4], even if it exists, because we care about everyone involved 
        hasDisease = [x for x in potentialContestants if x.hasThing(disease)]  # note some people here will be dead, but are still valid disease vectors (but shouldn't _catch_ a disease)
        if not hasDisease:
            return
        # Each person who already has the disease has a chance to spread it to every other person. I will pull it from the instance, in case in the future we have diseases with changing spread chances.
        for contestant in sorted(list(set(potentialContestants) - set(hasDisease)), key=lambda x: str(x)):
            if not contestant.alive:
                continue
            # Chance procs for each person already sick
            for sickPerson in hasDisease:
                if random.random() < DISEASE_ITEMS[disease]:
                    contestant.addStatus(disease)
                    thisWriter.addEvent(str(contestant)+" caught "+state["statuses"][disease].friendly+" from "+str(sickPerson), [contestant, state["statuses"][disease], sickPerson])
                    break

Item.registerInsertedCallback("postEventWriterCallbacks", spreadDisease)