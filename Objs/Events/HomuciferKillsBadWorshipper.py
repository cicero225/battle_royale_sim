
from Objs.Events.Event import Event
import random

def fixedHomuciferCallback(contestantKey, thisevent, state, participants, victims, sponsorsHere): 
    if thisevent.name == "HomuciferKillsBadWorshipper":
        del sponsorsHere[:] # Have to clear the list BUT keep the reference
        sponsorsHere.append(state["sponsors"]["Akuma Homura"])
    return True, False
    
Event.registerInsertedCallback("overrideContestantEvent", fixedHomuciferCallback)

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    success = random.randint(0,1)
    if success:
        mainActor.alive = False
        desc = sponsors[0].name+' struck down '+mainActor.name + " for "+Event.parseGenderPossessive(mainActor)+" dangerous beliefs."
        tempList = [sponsors[0], mainActor]
        del state["events"]["AWorshipsB"].eventStore[mainActor.name]
        deadList = [mainActor.name]
    else:
        desc = sponsors[0].name+' tried to strike down '+mainActor.name + " for "+Event.parseGenderPossessive(mainActor)+" dangerous beliefs, but Madokami was able to intervene successfully."
        tempList = [sponsors[0], mainActor, state["sponsors"]["Madokami"]]
        deadList = []
    return (desc, tempList, deadList) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("HomuciferKillsBadWorshipper", func)