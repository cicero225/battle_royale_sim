
from Objs.Events.Event import Event
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):    
    # Random relationship boost
    state["allRelationships"].IncreaseFriendLevel(mainActor.name, participants[0].name, random.randint(0,2)) 
    state["allRelationships"].IncreaseLoveLevel(mainActor.name, participants[0].name, random.randint(0,1))
    state["allRelationships"].IncreaseFriendLevel(participants[0].name, mainActor.name, random.randint(0,2))
    state["allRelationships"].IncreaseLoveLevel(participants[0].name, mainActor.name, random.randint(0,1))
    desc = mainActor.name+' and '+participants[0].name+' shared stories about their lives.'
    return (desc, [mainActor, participants[0]], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventShareStoryofLife = classmethod(func)

Event.registerEvent("ShareStoryofLife", Event.doEventShareStoryofLife)
