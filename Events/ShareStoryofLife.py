
from Events.Event import Event
import random

def func(Event, mainActor, state=None, participants=None, victims=None):
    # Hmm...having an object that takes care of this max 5 business would be nice    
    # Random relationship boost
    state["friendships"][mainActor.name][participants[0].name] = min(state["friendships"][mainActor.name][participants[0].name]+random.randint(0,2),5) 
    state["loveships"][mainActor.name][participants[0].name] = min(state["loveships"][mainActor.name][participants[0].name]+random.randint(0,1),5)
    state["friendships"][participants[0].name][mainActor.name] += min(state["friendships"][participants[0].name][mainActor.name]+random.randint(0,2),5)
    state["loveships"][participants[0].name][mainActor.name] += min(state["loveships"][participants[0].name][mainActor.name]+random.randint(0,1),5)
    desc = mainActor.name+' and '+participants[0].name+' shared stories about their lives.'
    return (desc, [mainActor.name, participants[0].name], []) # Second entry is the contestants named in desc, in order. Third is anyone who died. This is in strings.

Event.doEventShareStoryofLife = classmethod(func)

Event.registerEvent("ShareStoryofLife", Event.doEventShareStoryofLife)
