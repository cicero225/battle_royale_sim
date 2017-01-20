from Objs.Events.Event import Event
from Objs.Events.IndividualEventHandler import IndividualEventHandler

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    if state["items"]["Medicine"] in mainActor.inventory:
        mainActor.removeItem(state["items"]["Medicine"])
        desc = mainActor.name + " felt "+ Event.parseGenderReflexive(mainActor) + " getting sick, but was able to ward it off with " + Event.parseGenderPossessive(mainActor) + " medicine."
    else:
        mainActor.permStatChange({'stability': -1,
                                  'endurance': -3,
                                  'combat ability': -3})
        desc = mainActor.name + " gets sick with a severe fever."
        eventHandler = IndividualEventHandler(state)
        eventHandler.setEventWeightForSingleContestant("RecoversFromFever", mainActor.name, 10)
        eventHandler.setEventWeightForSingleContestant("DiesFromFever", mainActor.name, 10)
        eventHandler.setEventWeightForSingleContestant("FriendGivesMedicine", mainActor.name, 10)
        eventHandler.banEventForSingleContestant("DiesFromFever", mainActor.name)
        self.eventStore[mainActor.name] = eventHandler #registers event chain
    return (desc, [mainActor], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("SickWithFever", func)
