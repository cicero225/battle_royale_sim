from Objs.Events.Event import Event
from Objs.Events.IndividualEventHandler import IndividualEventHandler


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    if mainActor.hasThing("Medicine"):
        mainActor.removeItem(state["items"]["Medicine"])
        desc = mainActor.name + " felt " + Event.parseGenderReflexive(
            mainActor) + " getting sick, but was able to ward it off with " + Event.parseGenderPossessive(mainActor) + " medicine."
    else:
        desc = mainActor.name + " got sick with a severe fever."
        mainActor.addStatus("Fever")
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, [mainActor, state["statuses"]["Fever"]], [])


Event.registerEvent("SickWithFever", func)
