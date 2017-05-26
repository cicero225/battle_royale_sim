from Objs.Events.Event import Event

def func(self, mainActor, state = None, participants = None, victims = None, sponsors = None):
        mainActor.permStatChange({"gregariousness": -1,
                                  "endurance": -1,
                                  "stability": -2})
        desc = mainActor.name+" was haunted by images of the things " +Event.parseGenderSubject(mainActor)+" had seen."
        return(desc, {mainActor}, [])
Event.registerEvent("PTSD", func)
