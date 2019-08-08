from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.removeStatus("Fever")
    desc = mainActor.name + " died from " + \
        Event.parseGenderPossessive(mainActor) + " fever!"
    mainActor.kill()
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, [mainActor], [mainActor.name])


Event.registerEvent("DiesFromFever", func)
