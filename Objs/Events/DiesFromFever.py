from Objs.Events.Event import Event

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.removeStatus("Fever")
    desc = mainActor.name + " died from "+Event.parseGenderPossessive(mainActor)+" fever!"
    mainActor.alive = False
    return (desc, [mainActor], [mainActor.name]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("DiesFromFever", func)
