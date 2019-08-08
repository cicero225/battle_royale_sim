from __future__ import division

from Objs.Events.Event import Event
from Objs.Items.Status import StatusInstance
import random
from collections import defaultdict
from math import exp

# Survivalism, etc. shouldn't be included in the event weights, because this is kind of a neutral event.


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    success = True
    # It's okay to overwrite since we only care if it happened this turn
    self.eventStore.setdefault('turnRecord', defaultdict(
        lambda: -1))[mainActor.name] = state["turnNumber"][0]
    if str(mainActor) not in self.eventStore or not self.eventStore[str(mainActor)]:
        # base is 50%. unless the character has already done it before in which case success is assured
        # Yes this can overload past 1
        chanceSuccess = mainActor.stats["cleverness"] * \
            0.02 + mainActor.stats["survivalism"] * 0.05 + 0.5
        if random.random() > chanceSuccess:
            desc = str(mainActor) + ' tried to start a fire, but failed.'
            descList = [mainActor, state["statuses"]["Hypothermia"]]
            mainActor.addStatus(state["statuses"]["Hypothermia"].makeInstance(
                data={"day": state["turnNumber"][0]}))
            return (desc, descList, [])

    desc = str(mainActor) + ' successfully started a fire.'
    mainActor.removeStatus("Hypothermia")
    self.eventStore[str(mainActor)] = True

    # If character has ever killed anyone, initial 1/3 chance this becomes a haunting event. (affected by stability)
    # logistic
    hauntprob = 1/(1 + exp(3 - len(state["callbackStore"]["killCounter"][str(mainActor)]) + (mainActor.stats["stability"] - 5) * self.settings['statInfluence'] * 0.4))
    if state["callbackStore"]["killCounter"][str(mainActor)] and random.random() < hauntprob:
        haunter = state["contestants"][str(random.choice(state["callbackStore"]["killCounter"][str(mainActor)]))]
        desc = str(mainActor) + " was haunted by the ghost of " + str(haunter) + " and unable to sleep or make a fire."
        descList = [mainActor, state["statuses"]["Ghost"], haunter, state["statuses"]["Hypothermia"]]
        mainActor.addStatus(state["statuses"]["Hypothermia"].makeInstance(
                data={"day": state["turnNumber"][0]}))
        mainActor.permStatChange({"stability": random.randint(-2,0)})
        return (desc, descList, [])
    
    # Unless character already has clean water, 50% chance (potentially of the remaining 2/3) this becomes a clean water event
    if not mainActor.hasThing("Clean Water"):
        if random.random() > 0.5:
            desc += ' Using it, ' + \
                Event.parseGenderSubject(mainActor) + \
                ' was able to boil some Clean Water.'
            mainActor.addItem(state["items"]["Clean Water"], isNew=True)
            descList = [mainActor, state["items"]["Clean Water"]]
            return (desc, descList, [])

    # 50% chance here that nothing happens, unless it just ain't possible for something to happen (other participant must not have already done this event this turn or already have a fire)
    possibleFireSharers = [x for x in state["contestants"].values(
    ) if x.alive and not self.eventStore["turnRecord"][x.name] == state["turnNumber"][0]]
    if not possibleFireSharers or random.random() > 0.5:
        desc += ' ' + Event.parseGenderSubject(mainActor).capitalize(
        ) + ' was able to spend the night in comfort.'
        descList = [mainActor]
        return (desc, descList, [])

    # If someone finds them. Roll random contestant.
    contestant = random.choice(possibleFireSharers)
    desc += ' ' + contestant.name + ' found the fire'
    descList = [mainActor, contestant]

    # Use friendship and the other person's aggression/ruthlessness to determine what happens
    # Do they invite them to fire? - certain above 1 friendship or love, more ambivalent from -2 to 0, no below. Ruthlessness factors in.
    if ((state["allRelationships"].friendships[str(mainActor)][str(contestant)] > 0 and state["allRelationships"].loveships[str(mainActor)][str(contestant)] > 0)
        or (state["allRelationships"].friendships[str(mainActor)][str(contestant)] > -3 and state["allRelationships"].loveships[str(mainActor)][str(contestant)] > -3
            and random.random() < ((min(state["allRelationships"].friendships[str(mainActor)][str(contestant)], state["allRelationships"].loveships[str(mainActor)][str(contestant)]) + 3) / 3 - mainActor.stats["ruthlessness"] / 15))):
        desc += ', and they agreed to share the fire together.'
        self.eventStore["turnRecord"][contestant.name] = state["turnNumber"][0]
        contestant.removeStatus("Hypothermia")
        state["allRelationships"].IncreaseFriendLevel(
            mainActor, contestant, random.randint(0, 1))
        state["allRelationships"].IncreaseLoveLevel(
            mainActor, contestant, random.randint(0, 1))
        state["allRelationships"].IncreaseFriendLevel(
            contestant, mainActor, random.randint(1, 3))
        state["allRelationships"].IncreaseLoveLevel(
            contestant, mainActor, random.randint(0, 2))
        return (desc, descList, [])

    desc += ', but ' + mainActor.name + ' refused to let ' + \
        Event.parseGenderObject(contestant) + ' share it.'

    # Does the other party decide to attack? Only if friendship and loveship<0
    if ((state["allRelationships"].friendships[str(contestant)][str(mainActor)] > 0 and state["allRelationships"].loveships[str(contestant)][str(mainActor)] > 0)
            or random.random() > (contestant.stats["aggression"] * 2 + contestant.stats["ruthlessness"]) * abs(state["allRelationships"].friendships[str(contestant)][str(mainActor)] + 2 * state["allRelationships"].loveships[str(contestant)][str(mainActor)]) / 450):
        desc += ' After a moment, ' + contestant.name + ' left.'
        return (desc, descList, [], [], [mainActor])

    desc += ' After a moment, ' + contestant.name + ' attacked. A fight started, '
    (fightDesc, fightDescList, fightDeadList, allKillers) = Event.fight(
        descList, state["allRelationships"], state["settings"], deferActualKilling=True)
    # Special: if only one loser, 33% chance the loser escapes injured instead, losing loot.
    if len(fightDeadList) == 1:
        if random.random() > 0.33:
            # kill him anyway.
            fightDeadList[0].kill()
        else:
            # Injure the loser and divert the event outcome
            fightDeadList[0].addStatus(state["statuses"]["Injury"])
            if fightDeadList[0] == mainActor:
                self.eventStore["turnRecord"][contestant.name] = state["turnNumber"][0]
                desc += ' and ' + mainActor.name + ' was injured and forced to flee.'
                mainActor.addStatus(state["statuses"]["Hypothermia"].makeInstance(
                    data={"day": state["turnNumber"][0]}))
                contestant.removeStatus("Hypothermia")
                if fightDescList:
                    desc += ' ' + Event.parseGenderSubject(mainActor).capitalize(
                    ) + ' left behind ' + Event.englishList(fightDescList) + '.'
            else:
                desc += ' but ' + contestant.name + ' was injured and forced to flee.'
                contestant.addStatus(state["statuses"]["Hypothermia"].makeInstance(
                    data={"day": state["turnNumber"][0]}))
                if fightDescList:
                    desc += ' ' + Event.parseGenderSubject(contestant).capitalize(
                    ) + ' left behind ' + Event.englishList(fightDescList) + '.'
            descList.extend(fightDescList)
            return (desc, descList, [])

    # If nobody was hurt, they just give up and use the fire together.
    if not fightDeadList:
        self.eventStore["turnRecord"][contestant.name] = state["turnNumber"][0]
        contestant.removeStatus("Hypothermia")
        desc += ' but in the end both sides got tired and gave up, agreeing to use the fire together for one night. Neither side slept well.'
        return (desc, descList, [])

    # need to ban contestant from turning up again in fire events if they won the fight.
    if contestant.name not in fightDeadList:
        self.eventStore["turnRecord"][contestant.name] = state["turnNumber"][0]
    desc += fightDesc
    descList += fightDescList
    return (desc, descList, [x.name for x in fightDeadList], allKillers)


Event.registerEvent("MakeCampfire", func)
