# The Event class provides the generic framework for in-game events, providing the main structure common to all events.
# Because Events can have arbitrary effects, each event defined must have a .py file that extends this class, registering
# a callback for the delegator doEvent with the convenience function registerEvent, provided below.

# Note that it is very likely feasible to define some helper methods (like kill_player) here that events can call for common
# shared events.

from __future__ import division

import random
from collections import defaultdict, OrderedDict
from ..Utilities.ArenaUtils import weightedDictRandom, DictToOrderedDict, DefaultOrderedDict
from functools import partial
from Objs.Items.Item import ItemInstance


class Event(object):  # Python 2.x compatibility

    # It is important that this is a class attribute, which can be modified in Python
    event_callbacks = OrderedDict()
    # Some events need to place callbacks in main. Place here at import time. key -> callback location, value-> callback
    inserted_callbacks = OrderedDict()
    # This allows import time access to a pointer to state, which is needed occasionally by doEvent functors. It must be supplied by main during initialization.
    stateStore = [None]

    def __init__(self, name, inDict, settings):
        # Hey, it's the most straightforward way and basically achieves the purpose
        self.baseProps = inDict
        # Could also use setattr, but...

        # mainWeight = sets relative probability of rolling event for given character, participantWeight
        # sets probability of any given other contestant getting involved, victimWeight sets probability
        # of any given contestant being the victim, and sponsorWeight set probabiltiy of a given sponsor being the sponsor

        # modifier values list the contestant stats that affect the probabilities of these and by how relatively much (though
        # usually just 1 or -1). If there is a good way to make the json thing give dict(string)->float instead that'd be
        # preferred

        # Randomize baseWeight a little
        self.name = name
        # screw it, everyone gets a copy of what they need. Python stores by reference anyway.
        self.settings = settings
        # This is kind of a dumb way to do it, but being more general is a pain
        for multiplierType in ['main', 'participant', 'victim']:
            if multiplierType + 'Weight' in self.baseProps:
                self.eventRandomize(multiplierType + 'Weight')
        self.doEvent = partial(self.event_callbacks[self.name], self)
        # arbitrary storage for event data, useful for holding information over multiple calls
        self.eventStore = OrderedDict()

    def __str__(self):
        return self.name

    @classmethod
    def registerInsertedCallback(cls, callbackLocation, callback):
        cls.inserted_callbacks.setdefault(
            callbackLocation, []).append(callback)

    @classmethod
    def registerEvent(cls, eventName, callback):
        cls.event_callbacks[eventName] = callback

    def doEvent(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
        desc = mainActor.name + ' did absolutely nothing.'
        # Second entry is the contestants named in desc, in order. Third is anyone who died.
        return (desc, [mainActor], [])

    def eventRandomize(self, propName):
        self.baseProps[propName] = (self.baseProps[propName]
                                    * (1 + random.uniform(-1 * self.settings['eventRandomness'], self.settings['eventRandomness'])))

    @staticmethod
    def parseGenderSubject(contestantObj):
        genString = contestantObj.gender
        if genString == "F":
            return "she"
        elif genString == "M":
            return "he"
        else:
            return "it"

    @staticmethod
    def parseGenderObject(contestantObj):
        genString = contestantObj.gender
        if genString == "F":
            return "her"
        elif genString == "M":
            return "him"
        else:
            return "it"

    @staticmethod
    def parseGenderPossessive(contestantObj):
        genString = contestantObj.gender
        if genString == "F":
            return "her"
        elif genString == "M":
            return "his"
        else:
            return "its"

    @staticmethod
    def parseGenderReflexive(contestantObj):
        genString = contestantObj.gender
        if genString == "F":
            return "herself"
        elif genString == "M":
            return "himself"
        else:
            return "itself"

    @staticmethod
    def activateEventNextTurnForContestant(eventName, contestantName, state, weight):
        def func(actor, origWeight, event):
            if event.name == eventName and actor.name == contestantName:
                return (weight, True)
            else:
                return (origWeight, True)

        # this anonymizes func, giving a new reference each this is called
        def anonfunc(actor, origWeight, event): return func(
            actor, origWeight, event)
        # This needs to be at beginning for proper processing
        state["callbacks"]["modifyIndivActorWeights"].insert(0, anonfunc)
        # If you ever intend to remove this callback, it's a good idea to keep track of this.
        return anonfunc

    # TODO : We do not yet properly handle loot with potential different properties (i.e. two different non-stackable spears)
    @staticmethod
    def lootAll(looter, looted):
        if hasattr(looted, 'inventory'):
            itemList = [x for x in looted.inventory if x.lootable]
        else:
            itemList = [ItemInstance.takeOrMakeInstance(x) for x in looted if x.lootable]
        lootList = []
        for loot in itemList:
            if hasattr(looted, 'inventory'):
                looted.removeItem(loot, loot.count)
            # If we wanted to make non-stackable loot acquirable in mass quantity, we'd remove the first check...but what do you even do with two spears?...and it would cause double stats, etc.
            if not looter.hasThing(loot) or loot.stackable:
                lootref = looter.addItem(loot, loot.count, isNew=False)
                if lootref is None:
                    # We actually have to return it to keep the object from disappearing
                    looted.addItem(loot, loot.count, isNew=False)
                else:
                    lootList.append(lootref)
        return lootList

    @staticmethod
    def lootRandom(looters, looted):
        if hasattr(looted, 'inventory'):
            itemList = [x for x in looted.inventory if x.lootable]
        else:
            itemList = [ItemInstance.takeOrMakeInstance(x) for x in looted if x.lootable]
        lootList = []
        for loot in itemList:
            if hasattr(looted, 'inventory'):
                looted.removeItem(loot, loot.count)
            maybeLooters = [looter for looter in looters if not looter.hasThing(
                loot) or loot.stackable]
            if maybeLooters:
                for _ in range(loot.count):
                    # TODO : We do not yet properly handle loot with potential different properties (i.e. two different non-stackable spears). That means the name output here is incorrect.
                    trueLooter = random.choice(maybeLooters)
                    lootref = trueLooter.addItem(loot, isNew=False)
                    if lootref is None:
                        # We actually have to return it to keep the object from disappearing, and retrying this random.choice loop is risky
                        looted.addItem(lootref, isNew=False)
                    elif lootList and lootList[-1].name != loot.name:
                        lootList.append(loot)
        return lootList

    @staticmethod
    # Attacker, victim
    def DieOrEscapeProb1v1(person1, person2, settings, attackStat=None, defenseStat=None):
        if attackStat is None:
            attackStat = person1.getCombatAbility(person2)
        if defenseStat is None:
            defenseStat = person2.getCombatAbility(person1)
        # probability of kill
        return 1 / (1 + (1 + settings['combatAbilityEffect'])**(attackStat - defenseStat))

    @staticmethod
    def fight(people, relationships, settings):
        # Everyone who was injured to start with, so they shoulnd't be considered for being injured again.
        alreadyInjured = sorted(
            list(set(str(person) for person in people if person.hasThing("Injury"))))
        # Relationship changes
        # Fights shouldn't cause everyone's mutual friendship to go down, because sometimes it might be 2v2, but this is really hard to model, so rng
        relHitNum = random.randint(1, len(people) - 1)
        for person in people:
            relDict = DictToOrderedDict({i: 6 - (relationships.friendships[x.name][person.name] + relationships.friendships[person.name][x.name] + 2 * (
                relationships.loveships[person.name][x.name] + relationships.loveships[x.name][person.name])) / 6 for i, x in enumerate(people) if x != person})
            chosen = weightedDictRandom(relDict, relHitNum)
            for index in chosen:
                relationships.IncreaseFriendLevel(
                    person, people[index], random.randint(-4, -3))
                relationships.IncreaseLoveLevel(
                    person, people[index], random.randint(-6, -4))
        # Actual fight
        fightDict = OrderedDict()
        # people gain strength from their friends, but this has to be compared with the average strength of the rest of the group
        for i, person1 in enumerate(people):
            # includes a small multiplier from ruthlessness and aggression
            baseCombatAbility = person1.stats['combat ability'] * (1 + (
                (person1.stats['aggression'] * 2 + person1.stats['ruthlessness']) / 15 - 1) * 0.3)
            for person2 in people:
                if person1 == person2:
                    continue
                person2Ability = person2.stats['combat ability'] * (1 + (
                    (person2.stats['aggression'] * 2 + person2.stats['ruthlessness']) / 15 - 1) * 0.3)
                baseCombatAbility += settings['friendCombatEffect'] * relationships.friendships[str(person2)][str(
                    person1)] / 5 * person2Ability if relationships.friendships[str(person2)][str(person1)] > 0 else 0
                baseCombatAbility += settings['friendCombatEffect'] * relationships.loveships[str(person2)][str(
                    person1)] / 5 * person2Ability if relationships.loveships[str(person2)][str(person1)] > 0 else 0
            fightDict[i] = baseCombatAbility
        probDict = OrderedDict()
        deadList = []
        liveList = []
        injuredList = []
        for i, person1 in enumerate(people):
            meanAbilityTot = 0
            for ii, person2 in enumerate(people):
                if person1 == person2:
                    continue
                meanAbilityTot += fightDict[ii]
            # Sigmoid probability! woo...
            probDeath = 1 / (1 + (1 + settings['combatAbilityEffect'])**(
                fightDict[i] - meanAbilityTot / (len(people) - 1)))
            # Yes the exact same formula... because it makes sense.
            probInjury = 1 / (1 + (1 + settings['combatAbilityEffect'])**(
                fightDict[i] - meanAbilityTot / (len(people) - 1)))
            if random.random() < probDeath:
                deadList.append(person1)
                person1.alive = False
            else:
                liveList.append(person1)
                if str(person1) not in alreadyInjured and random.random() < probInjury:
                    injuredList.append(person1)
                    person1.addStatus(
                        Event.stateStore[0]["statuses"]["Injury"])
        if not deadList:
            desc = 'but no one was killed.'
            if injuredList:
                desc += ' (Injured: ' + Event.englishList(injuredList) + ')'
            return(desc, [], [], None)
        desc = 'and '
        descList = []
        if len(deadList) < len(people):
            lootList = []
            for theDead in deadList:
                lootList += Event.lootRandom(liveList, theDead)
            if len(deadList) == 1:
                desc += deadList[0].name + ' was killed!'
            else:
                desc += Event.englishList(deadList) + ' were killed!'
            if lootList:
                desc += ' ' + Event.englishList(lootList) + ' was looted.'
            descList.extend(lootList)
        elif len(deadList) == len(people):
            desc += 'everyone died in the fighting!'
        if injuredList:
            desc += ' (Injured: ' + Event.englishList(injuredList) + ')'
        # decide a killer for anyone killed. This is unusual and needs to be handled here
        allKillers = defaultdict(str)
        for dead in deadList:
            killDict = DictToOrderedDict({x: 1.1**(relationships.friendships[str(x)][str(
                dead)] + 2 * relationships.loveships[str(x)][str(dead)]) for x in people if x is not dead})
            allKillers[str(dead)] = str(weightedDictRandom(killDict)[0])
        return(desc, descList, deadList, allKillers)

    @staticmethod
    def factionFight(faction1, faction2, relationships, settings):
        # Everyone who was injured to start with, so they shoulnd't be considered for being injured again.
        alreadyInjured = sorted(list(
            set(str(person) for person in faction1 + faction2 if person.hasThing("Injury"))))
        # Relationship changes
        for person1 in faction1:
            for person2 in faction2:
                relationships.IncreaseFriendLevel(
                    person1, person2, random.randint(-4, -3))
                relationships.IncreaseLoveLevel(
                    person1, person2, random.randint(-6, -4))
                relationships.IncreaseFriendLevel(
                    person2, person1, random.randint(-4, -3))
                relationships.IncreaseLoveLevel(
                    person2, person1, random.randint(-6, -4))
        # Actual fight
        faction1Power = 0
        for person1 in faction1:
            # includes a small multiplier from ruthlessness and aggression
            faction1Power += person1.stats['combat ability'] * (1 + (
                (person1.stats['aggression'] * 2 + person1.stats['ruthlessness']) / 15 - 1) * 0.3)
        faction2Power = 0
        for person2 in faction2:
            # includes a small multiplier from ruthlessness and aggression
            faction2Power += person2.stats['combat ability'] * (1 + (
                (person2.stats['aggression'] * 2 + person2.stats['ruthlessness']) / 15 - 1) * 0.3)

        faction1ProbDeath = 1 / \
            (1 + (1 + settings['combatAbilityEffect'])
             ** (faction1Power - faction2Power))
        faction1ProbInjury = 1 / \
            (1 + (1 + settings['combatAbilityEffect'])
             ** (faction1Power - faction2Power))
        faction2ProbDeath = 1 / \
            (1 + (1 + settings['combatAbilityEffect'])
             ** (faction2Power - faction1Power))
        faction2ProbInjury = 1 / \
            (1 + (1 + settings['combatAbilityEffect'])
             ** (faction1Power - faction2Power))
        faction1DeadList = []
        faction1LiveList = []
        faction2DeadList = []
        faction2LiveList = []
        injuredList = []
        for person1 in faction1:
            # Sigmoid probability! woo...
            if random.random() < faction1ProbDeath:
                faction1DeadList.append(person1)
                person1.alive = False
            else:
                faction1LiveList.append(person1)
                if str(person1) not in alreadyInjured and random.random() < faction1ProbInjury:
                    injuredList.append(person1)
                    person1.addStatus(
                        Event.stateStore[0]["statuses"]["Injury"])
        for person2 in faction2:
            if random.random() < faction2ProbDeath:
                faction2DeadList.append(person2)
                person2.alive = False
            else:
                faction2LiveList.append(person2)
                if str(person2) not in alreadyInjured and random.random() < faction2ProbInjury:
                    injuredList.append(person2)
                    person2.addStatus(
                        Event.stateStore[0]["statuses"]["Injury"])

        if not faction1DeadList and not faction2DeadList:
            desc = 'but no one was killed.'
            if injuredList:
                desc += ' (Injured: ' + Event.englishList(injuredList) + ')'
            return(desc, [], [], OrderedDict())
        desc = 'and '
        descList = []
        deadList = faction1DeadList + faction2DeadList
        if len(deadList) < len(faction1) + len(faction2):
            # We have to do the looting carefully
            lootList1 = []
            for theDead in faction1DeadList:
                if not faction2LiveList:  # If the entire other faction is dead, this faction gets their own dead teammate's stuff
                    lootList1 += Event.lootRandom(faction1LiveList, theDead)
                else:
                    lootList1 += Event.lootRandom(faction2LiveList, theDead)
            lootList2 = []
            for theDead in faction2DeadList:
                if not faction1LiveList:
                    lootList2 += Event.lootRandom(faction2LiveList, theDead)
                else:
                    lootList2 += Event.lootRandom(faction1LiveList, theDead)
            lootList = lootList1 + lootList2
            if len(deadList) == 1:
                desc += deadList[0].name + ' was killed!'
            else:
                desc += Event.englishList(deadList) + ' were killed!'
            if lootList:
                desc += ' ' + Event.englishList(lootList) + ' was looted.'
            descList.extend(lootList)
        elif not faction2LiveList and not faction1LiveList:
            desc += 'everyone died in the fighting!'
        # decide a killer for anyone killed. This is unusual and needs to be handled here
        allKillers = DefaultOrderedDict(str)
        for dead in faction1DeadList:
            killDict = DictToOrderedDict({x: 1.1**(relationships.friendships[str(x)][str(
                dead)] + 2 * relationships.loveships[str(x)][str(dead)]) for x in faction2})
            allKillers[str(dead)] = str(weightedDictRandom(killDict)[0])
        for dead in faction2DeadList:
            killDict = DictToOrderedDict({x: 1.1**(relationships.friendships[str(x)][str(
                dead)] + 2 * relationships.loveships[str(x)][str(dead)]) for x in faction1})
            allKillers[str(dead)] = str(weightedDictRandom(killDict)[0])
        if injuredList:
            desc += ' (Injured: ' + Event.englishList(injuredList) + ')'
        return(desc, descList, deadList, allKillers)

    @staticmethod
    def getFriendlyIfPossible(namedObject):
        try:
            countModifier = " (x" + str(namedObject.count) + ")" if hasattr(
                namedObject, "count") and namedObject.count > 1 else ""
        except TypeError:
            countModifier = ""
        try:
            return namedObject.friendly + countModifier
        except AttributeError:
            return namedObject.name + countModifier

    @staticmethod
    def englishList(thingList, isObjs=True, customStringGetter=None):
        if customStringGetter:
            stringGetter = customStringGetter
        else:
            if isObjs:
                stringGetter = Event.getFriendlyIfPossible
            else:
                def stringGetter(x): return x
        if not thingList:
            return ''
        thingList = list(thingList)
        if len(thingList) == 1:
            return stringGetter(thingList[0])
        elif len(thingList) == 2:
            return stringGetter(thingList[0]) + ' and ' + stringGetter(thingList[1])
        else:
            return ', '.join(stringGetter(x) for x in thingList[:-1]) + ' and ' + stringGetter(thingList[-1])
