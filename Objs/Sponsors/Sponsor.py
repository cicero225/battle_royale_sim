
from __future__ import division # In case of Python 2+. The Python 3 implementation is way less dumb.
from ..Contestants.Contestant import Contestant

def contestantIndivActorWithSponsorsCallback(_, sponsor, baseEventSponsorWeight, event):
    try:
        addition = sponsor.eventAdditions[event.name]["sponsor"]
    except KeyError:
        addition = 0
    
    try:
        multiplier = sponsor.fullEventMultipliers[event.name]["sponsor"]
    except KeyError:
        multiplier = 1
    return (baseEventSponsorWeight*multiplier+addition, True)

class Sponsor(Contestant):  # sponsors are so similar to Contestants that it's easiest just to subclass. Really, though, they should both be inheriting from a more general parent class...
    
    # this is the main thing that needs overriding (mostly to be simpler)
    def InitializeEventModifiers(self, events): # Note that each event carries information about which stats affect them
        # This mixing of classes is regrettable but probably necessary
        self.events = events
        for eventName, event in self.events.items():
            #This is kind of a dumb way to do it, but being more general is a pain
            multiplierType = 'sponsor'
            self.eventAdditions[eventName][multiplierType] = 0
            if multiplierType+'Modifiers' in event.baseProps:
                self.statEventMultipliers[eventName][multiplierType] = 1
                for modifier, multiplier in event.baseProps[multiplierType+'Modifiers'].items():
                    self.statEventMultipliers[eventName][multiplierType] *= (1+self.settings['statInfluence'])**((self.stats[modifier]-5)*multiplier)
                self.fullEventMultipliers[eventName][multiplierType] = self.statEventMultipliers[eventName][multiplierType]
    
    