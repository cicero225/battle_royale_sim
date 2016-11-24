# Unlike the other main classes, the Event object is mostly not directly used, since events can have arbitrary effects.
# Instead, Event serves as the parent class for all other types of events, providing most of the structure but leaving
# the key method(s) for those event subtypes to determine. On its own, Event serves a default "does nothing" event.

# Yes, I know the trend nowadays is composition >> inheritance but _in this case_ it's extremely logical inheritance,
# and we'll probably never need to replace the parent class of any event. (Murphy's law: yes we will)

# Note that it is very likely feasible to define some helper methods (like kill_player) here that events can call for common
# shared events.

import random

class Event(object): #Python 2.x compatibility
    
    def __init__(self, name, inDict, settings):
        self.baseProps = inDict # Hey, it's the most straightforward way and basically achieves the purpose
        # Should be: float mainWeight, float optional participantWeight, float optional victimWeight, int numParticipants, int numVictims, bool unique
        # Randomize baseWeight a little
        self.name = name
        self.eventRandomize('mainWeight',settings)
        if 'participantWeight' in self.baseProps:
            self.eventRandomize('participantWeight',settings)
        if 'victimWeight' in self.baseProps:
            self.eventRandomize('victimWeight',settings)
        
    def doEvent(self,*args,**kwargs): # args allows passing of arbitrary number of contestants (or other arguments), kwargs allows passing of specific args
        # like settings. The default doEvent expects one contestant
        desc = args[0].name+' did absolutely nothing.'
        return desc
    
    def eventRandomize(propName, settings):
        self.baseProps[propName] = self.baseProps[propName]*(1+random.uniform(-1*settings['eventRandomness'],settings['eventRandomness']))