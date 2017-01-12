# The Event class provides the generic framework for in-game events, providing the main structure common to all events.
# Because Events can have arbitrary effects, each event defined must have a .py file that extends this class, registering
# a callback for the delegator doEvent with the convenience function registerEvent, provided below.

# Note that it is very likely feasible to define some helper methods (like kill_player) here that events can call for common
# shared events.

import random
from ..Utilities.ArenaUtils import weightedDictRandom

class Event(object): #Python 2.x compatibility

    event_callbacks = {}  # It is important that this is a class attribute, which can be modified in Python

    def __init__(self, name, inDict, settings):
        self.baseProps = inDict # Hey, it's the most straightforward way and basically achieves the purpose
        # Could also use setattr, but...
        # Should be: float mainWeight, float optional participantWeight, float optional victimWeight,
        # int optional numParticipants, int optional numVictims, dict (string: float) mainModifiers,
        # int optional numParticipantsExtra, int optional numVictimsExtra, int optional numSponsorsExtra <- if there is some squishiness to the number of participants/victims
        # dict (string: float) optional participantModifiers, dict (string: float) optional victimModifiers,
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
        # If first bool is true, then you need friendship level > (or if bool false, <) the specified needed level
        # bool optional friendRequiredParticipant, (relation: bool, value:int) optional neededFriendLevelParticipant 
        # bool optional loveRequiredParticipant, (relation: bool, value:int) optional, neededLoveLevelParticipant
        # bool optional friendRequiredVictim, (relation: bool, value:int) optional neededFriendLevelVictim
        # bool optional loveRequiredVictim, (relation: bool, value:int) optional, neededLoveLevelVictim
        # bool optional friendRequiredSponsor, (relation: bool, value:int) optional neededFriendLevelSponsor
        # bool optional loveRequiredSponsor, (relation: bool, value:int) optional, neededLoveLevelSponsor

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
    
    @classmethod
    def registerEvent(cls, eventName, callback):
        cls.event_callbacks[eventName] = callback
    
    def doEvent(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
        if self.name in self.event_callbacks:
            callback = self.event_callbacks[self.name]
            return callback(mainActor, state, participants, victims, sponsors)
        else:
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
    def fight(people, relationships, settings):
        fightDict = {}
        for i, person1 in enumerate(people): # people gain strength from their friends, but this has to be compared with the average strength of the rest of the group
            baseCombatAbility = person1.stats['combat ability']
            for person2 in people:
                if person1 == person2:
                    continue
                baseCombatAbility += settings['friendCombatEffect']*relationships.friendships[person2][person1]/5 * person2.stats['combat ability'] if relationships.friendships[person2][person1]>0 else 0
                baseCombatAbility += settings['friendCombatEffect']*relationships.loveships[person2][person1]/5 * person2.stats['combat ability'] if relationships.loveships[person2][person1]>0 else 0
            fightDict[i]=baseCombatAbility
        probDict = {}
        deadList = []
        liveList =[]
        for i, person1 in enumerate(people):
            meanAbilityTot = 0
            for ii, person2 in enumerate(people):
                if person1 == person2:
                    continue
                meanAbilityTot += fightDict[ii]
            # Sigmoid probability! woo...
            probDeath = 1/(1+(1+settings['combatAbilityEffect'])**(fightDict[i]-meanAbilityTot/(len(people)-1)))
            if random.random()<probDeath:
                deadList.append(person1)
                person1.alive = False
            else:
                liveList.append(person1)
        if not deadList:
            desc = 'but no was was hurt.'
            return(desc, [], [])
        desc = 'and '
        descList = []
        if len(deadList) < len(people):
            for theDead in deadList:
                lootList = Event.lootRandom(liveList, theDead)
            if len(deadList) == 1:
                desc += deadList[0].name+' was killed!'
            else:
                desc += Event.englishList(deadList)+' were killed!'
            if lootList:
                desc += ' '+Event.englishList(lootList)+' was looted.'
            descList.extend(lootList)
        elif len(deadList) == len(people):
            desc += 'everyone died in the fighting!'
        return(desc, descList, deadList)
    
    @staticmethod
    def getFriendlyIfPossible(namedObject):
        try:
            return namedObject.friendly
        except AttributeError:
            return namedObject.name
    
    @staticmethod
    def englishList(thingList):
        if len(thingList) == 1:
            return Event.getFriendlyIfPossible(thingList[0])
        elif len(thingList) == 2:
            return Event.getFriendlyIfPossible(thingList[0]) + ' and ' + Event.getFriendlyIfPossible(thingList[1])
        else:
            return ', '.join(Event.getFriendlyIfPossible(x) for x in thingList[:-1])+' and '+Event.getFriendlyIfPossible(thingList[-1])