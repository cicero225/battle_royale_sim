# The Event class provides the generic framework for in-game events, providing the main structure common to all events.
# Because Events can have arbitrary effects, each event defined must have a .py file that extends this class, registering
# a callback for the delegator doEvent with the convenience function registerEvent, provided below.

# Note that it is very likely feasible to define some helper methods (like kill_player) here that events can call for common
# shared events.

import random

class Event(object): #Python 2.x compatibility

    event_callbacks = {}  # It is important that this is a class attribute, which can be modified in Python

    def __init__(self, name, inDict, settings):
        self.baseProps = inDict # Hey, it's the most straightforward way and basically achieves the purpose
        # Could also use setattr, but...
        # Should be: float mainWeight, float optional participantWeight, float optional victimWeight,
        # int optional numParticipants, int optional numVictims, dict (string: float) mainModifiers,
        # dict (string: float) optional participantModifiers, dict (string: float) optional victimModifiers,
        # bool unique, list[string] optional uniqueUsers #at the moment only supports unique contestants performing the event, rather than being the victim etc. This is bad for, say, Mami getting her head eaten.
        # bool itemRequired, string optional necessaryItem
        # (The event is more (or less) likely if actor has ANY relationship that meets the criterion >mainFriendLevel. Set bool to false if you want < instead.
        # float mainFriendEffect (set 0 for none), (relation: bool, value: int) mainNeededFriendLevel  
        # float mainLoveEffect (set 0 for none), (relation: bool, value:int) mainNeededLoveLevel
        # float friendEffect (set 0 for none) [FROM ACTOR to PARTICIPANT (except for >2 people, in which case all are checked)]
        # float loveEffect (set 0 for none)
        # float friendEffectVictim
        # float loveEffectVictim
        # If first bool is true, then you need friendship level > (or if bool false, <) the specified needed level
        # bool optional friendRequired, (relation: bool, value:int) optional neededFriendLevel 
        # bool optional loveRequired, (relation: bool, value:int) optional, neededLoveLevel
        # bool optional friendRequiredVictim, (relation: bool, value:int) optional neededFriendLevelVictim
        # bool optional loveRequiredVictim, (relation: bool, value:int) optional, neededLoveLevelVictim

        # mainWeight = sets relative probability of rolling event for given character, participantWeight
        # sets probability of any given other contestant getting involved, victimWeight sets probability
        # of any given contestant being the victim

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
    
    def doEvent(self, mainActor, state=None, participants=None, victims=None):
        if self.name in self.event_callbacks:
            callback = self.event_callbacks[self.name]
            return callback(mainActor, state, participants, victims)
        else:
            desc = mainActor.name+' did absolutely nothing.'
            return (desc, [mainActor], []) # Second entry is the contestants named in desc, in order. Third is anyone who died.

    def eventRandomize(self, propName):
        self.baseProps[propName] = (self.baseProps[propName]
                                    *(1+random.uniform(-1*self.settings['eventRandomness'], self.settings['eventRandomness'])))
