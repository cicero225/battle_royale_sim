
# I wonder if this needs to import Contestant...

class Item(object):

    def __init__(self, name, inDict, settings):
        # The item class has certain stereotyped effects on characters that can be encoded in json
        self.name = name
        self.friendly = inDict["friendly"] if "friendly" in inDict else self.name
        self.settings = settings
        # This dict (string:int) stores any direct additions/subtractions in stats given by the Item
        self.statChanges = inDict["statChanges"]
        # This dict (string: dict(string: float) stores any event multiplier effects given by the object. Keys are events, followed by main/participant/victim
        self.eventMultipliers = inDict["eventMultipliers"]
        # This dict (string: dict(string: float)) stores any event additive effects given by the object. Keys are events, followed by main/participant/victim
        self.eventAdditions = inDict["eventAdditions"] 
        # This dict (string: bool) stores any events actively disabled by this object. Keys are events, followed by main/participant/victim. If you don't want a subcategory disabled, you can not include a listing, or explicitly have a boolean
        self.eventsDisabled = inDict["eventsDisabled"]
        if settings["objectInfluence"] != 1:
            self.applyObjectInfluence(self.statChanges)
            self.applyObjectInfluence(self.eventMultipliers)
            self.applyObjectInfluence(self.eventAdditions)

    def applyObjectInfluence(self, inDict):
        for key in inDict:
            inDict[key] *= self.settings["objectInfluence"]

    def applyObjectStatChanges(self, contestant): # this has to be processed before anything else...
        for changedStat in self.statChanges:
            contestant.stats[changedStat] += self.statChanges[changedStat]

    def onAcquisition(self, contestant):
        for eventName, eventModifier in self.eventMultipliers.items():
            for actorType, modifier in eventModifier.items():
                contestant.fullEventMultipliers[eventName][actorType] *= modifier
        for eventName, eventModifier in self.eventAdditions.items():
            for actorType, modifier in eventModifier.items():
                contestant.eventAdditions[eventName][actorType] += modifier
        for eventName, eventModifier  in self.eventsDisabled.items():
            for actorType, modifier  in eventModifier.items():
                contestant.eventDisabled[eventName][actorType] = modifier
                
    def onRemoval(self, contestant):
        pass