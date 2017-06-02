from Objs.Events.Event import Event

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.permStatChange({'stability': 1,
                              'endurance': 3,
                              'combat ability': 3})
    desc = mainActor.name + " recovered from "+Event.parseGenderPossessive(mainActor)+" fever."
    if mainActor.hasThing("Medicine"):
        mainActor.removeItem(state["items"]["Medicine"])
        desc = "Thanks to "+Event.parseGenderPossessive(mainActor)+" medicine, "+desc
    del state["events"]["SickWithFever"].eventStore[mainActor.name]
    return (desc, [mainActor], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("RecoversFromFever", func)
