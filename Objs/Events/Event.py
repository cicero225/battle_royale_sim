# The Event class provides the generic framework for in-game events, providing the main structure common to all events.
# Because Events can have arbitrary effects, each event defined must have a .py file that extends this class, registering
# a callback for the delegator doEvent with the convenience function registerEvent, provided below.

# Note that it is very likely feasible to define some helper methods (like kill_player) here that events can call for common
# shared events.

from __future__ import division

import random
from collections import defaultdict
from ..Utilities.ArenaUtils import weightedDictRandom
from functools import partial

class Event(object): #Python 2.x compatibility

    event_callbacks = {}  # It is important that this is a class attribute, which can be modified in Python
    inserted_callbacks = {}  # Some events need to place callbacks in main. Place here at import time. key -> callback location, value-> callback
    stateStore = [None]  # This allows import time access to a pointer to state, which is needed occasionally by doEvent functors. It must be supplied by main during initialization.

    def __init__(self, name, inDict, settings):
        self.baseProps = inDict # Hey, it's the most straightforward way and basically achieves the purpose
        # Could also use setattr, but...
        # Should be: 
        # list(string) optional phase <- sets which phases the event is valid for (day, night, etc.). If this is not set, it is assumed it is always valid.
        # float mainWeight, float optional participantWeight, float optional victimWeight,
        # int optional numParticipants, int optional numVictims, int optional numSponsors, dict (string: float) mainModifiers,
        # int optional numParticipantsExtra, int optional numVictimsExtra, int optional numSponsorsExtra <- if there is some squishiness to the number of participants/victims
        # dict (string: float) optional participantModifiers, dict (string: float) optional victimModifiers, dict (string: float) optional sponsorModifiers
        # bool optional murder: indicates that an event can cause someone to kill someone, counting as a kill. Should not be used for sponsor kills or deaths with no killer.
        # bool unique, list[string] optional uniqueUsers #at the moment only supports unique contestants performing the event, rather than being the victim etc. This is bad for, say, Mami getting her head eaten.
        # bool itemRequired, string optional necessaryItem
        # (The event is more (or less) likely if actor has ANY relationship that meets the criterion >mainFriendLevel. Set bool to false if you want < instead.
        # These are optional if no corresponding victim, participant, or sponsor is actually involved in the event
        # float mainFriendEffect (set 0 for none), (relation: bool, value: int) mainNeededFriendLevel  
        # float mainLoveEffect (set 0 for none), (relation: bool, value:int) mainNeededLoveLevel
        # These cause events to be more likely ONLY if ACTOR and PARTICIPANT (OR VICTIM) share relationship. By default it only checks ACTOR -> PARTICIPANT
        # bool optional mutual # This causes relationship checking to act both ways (the usual use case)
        # bool optional reverse # This causes relationship checking to act backwards (usually only for sponsors)
        # float friendEffectParticipant (set 0 for none)
        # float loveEffectParticipant (set 0 for none)
        # float friendEffectVictim
        # float loveEffectVictim
        # float friendEffectSponsor
        # float loveEffectSponsor
        # float participantFriendEffectVictim -> Effect a friendship between participant and victim has on chance for participant to bail
        # float loveFriendEffectVictim
        # If first bool is true, then you need friendship level > (or if bool false, <) the specified needed level
        # bool optional friendRequiredParticipant, (relation: bool, value:int) optional neededFriendLevelParticipant 
        # bool optional loveRequiredParticipant, (relation: bool, value:int) optional, neededLoveLevelParticipant
        # bool optional friendRequiredVictim, (relation: bool, value:int) optional neededFriendLevelVictim
        # bool optional loveRequiredVictim, (relation: bool, value:int) optional, neededLoveLevelVictim
        # bool optional friendRequiredSponsor, (relation: bool, value:int) optional neededFriendLevelSponsor
        # bool optional loveRequiredSponsor, (relation: bool, value:int) optional, neededLoveLevelSponsor
        # bool optional participantFriendRequiredVictim, (relation: bool, value:int) optional, ParticipantNeededFriendLevelVictim
        # bool optional participantLoveRequiredVictim, (relation: bool, value:int) optional, ParticipantNeededLoveLevelVictim
        # bool murder whether or not deaths in this event should be interpreted as homicide by the kill logger
        # dict (string: dict(value: flout, all: bool)) - controls which sponsor traits respond to this event, and whether this applies to all participants or just the mainActor

        # mainWeight = sets relative probability of rolling event for given character, participantWeight
        # sets probability of any given other contestant getting involved, victimWeight sets probability
        # of any given contestant being the victim, and sponsorWeight set probabiltiy of a given sponsor being the sponsor

        # modifier values list the contestant stats that affect the probabilities of these and by how relatively much (though
        # usually just 1 or -1). If there is a good way to make the json thing give dict(string)->float instead that'd be
        # preferred

        # unique signals the event processor that only the characters listed in uniqueUsers may trigger this event

        # Randomize baseWeight a little
        self.name = name
        self.settings = settings #screw it, everyone gets a copy of what they need. Python stores by reference anyway.
        #This is kind of a dumb way to do it, but being more general is a pain
        for multiplierType in ['main', 'participant', 'victim']:
            if multiplierType+'Weight' in self.baseProps:
                self.eventRandomize(multiplierType+'Weight')
        self.doEvent = partial(self.event_callbacks[self.name], self)
        self.eventStore = {}  # arbitrary storage for event data, useful for holding information over multiple calls
    
    def __str__(self):
        return self.name
    
    @classmethod
    def registerInsertedCallback(cls, callbackLocation, callback):
        cls.inserted_callbacks.setdefault(callbackLocation, []).append(callback)
    
    @classmethod
    def registerEvent(cls, eventName, callback):
        cls.event_callbacks[eventName] = callback
    
    def doEvent(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
        desc = mainActor.name+' did absolutely nothing.'
        return (desc, [mainActor], []) # Second entry is the contestants named in desc, in order. Third is anyone who died.

    def eventRandomize(self, propName):
        self.baseProps[propName] = (self.baseProps[propName]
                                    *(1+random.uniform(-1*self.settings['eventRandomness'], self.settings['eventRandomness'])))
                                    
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
        anonfunc = lambda actor, origWeight, event: func(actor, origWeight, event) # this anonymizes func, giving a new reference each this is called
        state["callbacks"]["modifyIndivActorWeights"].insert(0, anonfunc) # This needs to be at beginning for proper processing
        return anonfunc # If you ever intend to remove this callback, it's a good idea to keep track of this.
    
    @staticmethod
    def lootAll(looter, looted):
        if hasattr(looted, 'inventory'):
            itemList = looted.inventory
        else:
            itemList = looted
        lootList = []
        for loot in itemList:
            if hasattr(looted, 'inventory'):
                looted.removeItem(loot)
            if loot not in looter.inventory:
                looter.addItem(loot)
                lootList.append(loot)
        return lootList
    
    @staticmethod
    def lootRandom(looters, looted):
        if hasattr(looted, 'inventory'):
            itemList = looted.inventory
        else:
            itemList = looted
        lootList = []
        for loot in itemList:
            if hasattr(looted, 'inventory'):
                looted.removeItem(loot)
            maybeLooters = [looter for looter in looters if loot not in looter.inventory]
            if maybeLooters:
                trueLooter = random.choice(maybeLooters)
                trueLooter.addItem(loot)
                lootList.append(loot)
        return lootList
    
    @staticmethod
    def DieOrEscapeProb1v1(person1, person2, settings, attackStat=None, defenseStat=None): # Attacker, victim
        if attackStat is None:
            attackStat = person1.stats['combat ability']
        if defenseStat is None:
            defenseStat = person2.stats['combat ability']
        return 1/(1+(1+settings['combatAbilityEffect'])**(attackStat-defenseStat)) # probability of kill
        
    @staticmethod
    def fight(people, relationships, settings):
        # Relationship changes
        # Fights shouldn't cause everyone's mutual friendship to go down, because sometimes it might be 2v2, but this is really hard to model, so rng
        relHitNum = random.randint(1,len(people)-1)
        for person in people:
            relDict = {i:6-(relationships.friendships[x.name][person.name]+relationships.friendships[person.name][x.name]+2*(relationships.loveships[person.name][x.name]+relationships.loveships[x.name][person.name]))/6 for i, x in enumerate(people) if x != person}
            chosen = weightedDictRandom(relDict, relHitNum)
            for index in chosen:
                relationships.IncreaseFriendLevel(person, people[index], random.randint(-4,-3))
                relationships.IncreaseLoveLevel(person, people[index], random.randint(-6,-4))  
        # Actual fight
        fightDict = {}
        for i, person1 in enumerate(people): # people gain strength from their friends, but this has to be compared with the average strength of the rest of the group
            baseCombatAbility = person1.stats['combat ability']*(1+((person1.stats['aggression']*2+person1.stats['ruthlessness'])/15 - 1)*0.3) # includes a small multiplier from ruthlessness and aggression
            for person2 in people:
                if person1 == person2:
                    continue
                person2Ability = person2.stats['combat ability']*(1+((person2.stats['aggression']*2+person2.stats['ruthlessness'])/15 - 1)*0.3)
                baseCombatAbility += settings['friendCombatEffect']*relationships.friendships[person2][person1]/5 * person2Ability if relationships.friendships[person2][person1]>0 else 0
                baseCombatAbility += settings['friendCombatEffect']*relationships.loveships[person2][person1]/5 * person2Ability if relationships.loveships[person2][person1]>0 else 0
            fightDict[i]=baseCombatAbility
        probDict = {}
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
            probDeath = 1/(1+(1+settings['combatAbilityEffect'])**(fightDict[i]-meanAbilityTot/(len(people)-1)))
            # Yes the exact same formula... because it makes sense.
            probInjury = 1/(1+(1+settings['combatAbilityEffect'])**(fightDict[i]-meanAbilityTot/(len(people)-1)))
            if random.random()<probDeath:
                deadList.append(person1)
                person1.alive = False
            else:
                liveList.append(person1)
                if random.random()<probInjury:
                    injuredList.append(person1)
                    person1.SetInjured()
        if not deadList:
            desc = 'but no one was killed.'
            if injuredList:
                desc += ' (Injured: '+Event.englishList(injuredList)+')'
            return(desc, [], [])
        desc = 'and '
        descList = []
        if len(deadList) < len(people):
            lootList = []
            for theDead in deadList:
                lootList += Event.lootRandom(liveList, theDead)
            if len(deadList) == 1:
                desc += deadList[0].name+' was killed!'
            else:
                desc += Event.englishList(deadList)+' were killed!'
            if lootList:
                desc += ' '+Event.englishList(lootList)+' was looted.'
            descList.extend(lootList)
        elif len(deadList) == len(people):
            desc += 'everyone died in the fighting!'
        if injuredList:
            desc += ' (Injured: '+Event.englishList(injuredList)+')'
        return(desc, descList, deadList)
    
    @staticmethod
    def factionFight(faction1, faction2, relationships, settings):
        # Relationship changes
        for person1 in faction1:
            for person2 in faction2:
                relationships.IncreaseFriendLevel(person1, person2, random.randint(-4,-3))
                relationships.IncreaseLoveLevel(person1, person2, random.randint(-6,-4))
                relationships.IncreaseFriendLevel(person2, person1, random.randint(-4,-3))
                relationships.IncreaseLoveLevel(person2, person1, random.randint(-6,-4))  
        # Actual fight
        faction1Power = 0
        for person1 in faction1:
            faction1Power += person1.stats['combat ability']*(1+((person1.stats['aggression']*2+person1.stats['ruthlessness'])/15 - 1)*0.3) # includes a small multiplier from ruthlessness and aggression
        faction2Power = 0
        for person2 in faction2:
            faction2Power += person2.stats['combat ability']*(1+((person2.stats['aggression']*2+person2.stats['ruthlessness'])/15 - 1)*0.3) # includes a small multiplier from ruthlessness and aggression
        
        faction1ProbDeath = 1/(1+(1+settings['combatAbilityEffect'])**(faction1Power-faction2Power))
        faction1ProbInjury = 1/(1+(1+settings['combatAbilityEffect'])**(faction1Power-faction2Power))
        faction2ProbDeath = 1/(1+(1+settings['combatAbilityEffect'])**(faction2Power-faction1Power))
        faction2ProbInjury = 1/(1+(1+settings['combatAbilityEffect'])**(faction1Power-faction2Power))
        faction1DeadList = []
        faction1LiveList = []
        faction2DeadList = []
        faction2LiveList = []
        injuredList = []
        for person1 in faction1:
            # Sigmoid probability! woo...
            if random.random()<faction1ProbDeath:
                faction1DeadList.append(person1)
                person1.alive = False
            else:
                faction1LiveList.append(person1)
                if random.random()<faction1ProbInjury:
                    injuredList.append(person1)
                    person1.SetInjured()
        for person2 in faction2:
            if random.random()<faction2ProbDeath:
                faction2DeadList.append(person2)
                person2.alive = False
            else:
                faction2LiveList.append(person2)
                if random.random()<faction2ProbInjury:
                    injuredList.append(person2)
                    person2.SetInjured()
                
        if not faction1DeadList and not faction2DeadList:
            desc = 'but no one was killed.'
            if injuredList:
                desc += ' (Injured: '+Event.englishList(injuredList)+')'
            return(desc, [], [], {})
        desc = 'and '
        descList = []
        deadList = faction1DeadList + faction2DeadList
        if len(deadList) < len(faction1) + len(faction2):
            # We have to do the looting carefully
            lootList1 = []
            for theDead in faction1DeadList:
                if not faction2LiveList: # If the entire other faction is dead, this faction gets their own dead teammate's stuff
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
                desc += deadList[0].name+' was killed!'
            else:
                desc += Event.englishList(deadList)+' were killed!'
            if lootList:
                desc += ' '+Event.englishList(lootList)+' was looted.'
            descList.extend(lootList)
        elif not faction2LiveList and not faction1LiveList:
            desc += 'everyone died in the fighting!'
        # decide a killer for anyone killed. This is unusual and needs to be handled here
        allKillers = defaultdict(str)
        for dead in faction1DeadList:
            killDict = {x:1.1**(relationships.friendships[str(x)][str(dead)]+2*relationships.loveships[str(x)][str(dead)]) for x in faction2}
            allKillers[str(dead)] = str(weightedDictRandom(killDict)[0])
        for dead in faction2DeadList:
            killDict = {x:1.1**(relationships.friendships[str(x)][str(dead)]+2*relationships.loveships[str(x)][str(dead)]) for x in faction1}
            allKillers[str(dead)] = str(weightedDictRandom(killDict)[0])
        if injuredList:
            desc += ' (Injured: '+Event.englishList(injuredList)+')'
        return(desc, descList, deadList, allKillers)
    
    @staticmethod
    def getFriendlyIfPossible(namedObject):
        try:
            return namedObject.friendly
        except AttributeError:
            return namedObject.name
    
    @staticmethod
    def englishList(thingList, isObjs=True, customStringGetter=None):
        if customStringGetter:
            stringGetter = customStringGetter
        else:
            if isObjs:
                stringGetter = Event.getFriendlyIfPossible
            else:
                stringGetter = lambda x: x
        if not thingList:
            return ''
        thingList = list(thingList)
        if len(thingList) == 1:
            return stringGetter(thingList[0])
        elif len(thingList) == 2:
            return stringGetter(thingList[0]) + ' and ' + stringGetter(thingList[1])
        else:
            return ', '.join(stringGetter(x) for x in thingList[:-1])+' and '+stringGetter(thingList[-1])
