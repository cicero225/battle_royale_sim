from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = mainActor.name + " recovered from " + \
        Event.parseGenderPossessive(mainActor) + " fever."
    if mainActor.hasThing("Medicine"):
        mainActor.removeItem(state["items"]["Medicine"])
        desc = "Thanks to " + \
            Event.parseGenderPossessive(mainActor) + " medicine, " + desc
    mainActor.removeStatus("Fever")
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, [mainActor], [])


Event.registerEvent("RecoversFromFever", func)
