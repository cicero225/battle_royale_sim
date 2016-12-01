
# I wonder if this needs to import Contestant...

class Item(object):
    
    def __init__(self, name, inDict, settings):
        # The item class has certain stereotyped effects on characters that can be encoded in json
        self.name = name
        self.settings = settings
        # This dict (string:int) stores any direct additions/subtractions in stats given by the Item
        self.statChanges = inDict["statChanges"]
        # This dict (string:float) stores any event multiplier effects given by the object
        self.eventMultipliers = inDict["eventMultipliers"]
        # This dict (string:float) stores any event additive effects given by the object
        self.eventAdditions = inDict["eventAdditions"]
        # This list (string) stores any events actively disabled by this object
        self.eventsDisabled = inDict["eventsDisabled"]
        if settings.objectInfluence != 1 :
            self.applyObjectInfluence(self.statChanges)
            self.applyObjectInfluence(self.eventMultipliers)
            self.applyObjectInfluence(self.eventAdditions)
    
    def applyObjectInfluence(self,inDict):
        for key in inDict:
            inDict[key] *= self.objectInfluence
    
    def applyObjectStatChanges(self,contestant): # this has to be processed before anything else...
        for changedStat in self.statChanges:
            contestant.stats[changedStat] += self.statChanges[changedStat]
    
    def onAcquisition(self, contestant):
        for changedStat in self.eventMultipliers:
            contestant.fullEventMultipliers *= self.eventMultipliers[changedStat]
        for changedStat in self.eventAdditions:
            contestant.fullEventMultipliers += self.eventAdditions[changedStat]
        for changedStat in self.eventsDisabled:
            contestant.eventDisabled[changedStat] = True
    
    def onRemoval(self, contestant):
        pass