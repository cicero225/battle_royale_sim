
from Objs.Events.Event import Event
import random

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    if state["allRelationships"].loveships[str(mainActor)][str(participants[0])]:
        desc = str(mainActor) + " offered to cook for " + str(participants[0]) + ", who gladly accepted. The meal was crafted with care and tenderness."
    else:
        desc = str(mainActor) + " offered to cook for " + str(participants[0]) + ", who gladly accepted. The meal was pretty good."
    state["allRelationships"].IncreaseFriendLevel(mainActor, participants[0], random.randint(1,3)) 
    state["allRelationships"].IncreaseLoveLevel(mainActor, participants[0], random.randint(0,2))
    state["allRelationships"].IncreaseFriendLevel(participants[0], mainActor, random.randint(1,3))
    state["allRelationships"].IncreaseLoveLevel(participants[0], mainActor, random.randint(0,2))  
    
    
    return (desc, [mainActor, participants[0]], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    
Event.registerEvent("ACooksForB", func)
