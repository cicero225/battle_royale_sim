
from Objs.Events.Event import Event
import random


def fixedMadokamiCallback(contestantKey, thisevent, state, participants, victims, sponsorsHere, alreadyUsed):
    if thisevent.name == "MadokamiKillsBadWorshipper":
        del sponsorsHere[:]  # Have to clear the list BUT keep the reference
        sponsorsHere.append(state["sponsors"]["Madokami"])
    return True, False


Event.registerInsertedCallback(
    "overrideContestantEvent", fixedMadokamiCallback)


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    success = random.randint(0, 1)
    if success:
        mainActor.alive.kill()
        desc = sponsors[0].name + ' struck down ' + mainActor.name + " for " + \
            Event.parseGenderPossessive(mainActor) + " blasphemous beliefs."
        tempList = [sponsors[0], mainActor]
        del state["events"]["AWorshipsB"].eventStore[mainActor.name]
        deadList = [mainActor.name]
    else:
        desc = sponsors[0].name + ' tried to strike down ' + mainActor.name + " for " + Event.parseGenderPossessive(
            mainActor) + " blasphemous beliefs, but Akuma Homura was able to intervene successfully."
        tempList = [sponsors[0], mainActor, state["sponsors"]["Akuma Homura"]]
        deadList = []
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, tempList, deadList)


Event.registerEvent("MadokamiKillsBadWorshipper", func)
