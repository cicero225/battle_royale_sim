from Event import *

# Extends class in place
class Event(Event):
    
    Event.registerEvent("EventTemplate",self.doEventEventTemplate) #I think this works, but might have to be in __init__
    
    def doEventEventTemplate(self, mainActor, state=None, participants=None, victims=None):
        pass