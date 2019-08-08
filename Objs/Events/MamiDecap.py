from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.kill()
    desc = mainActor.name + \
        " was decapitated by a trap due to carelessness and wanting to show off."
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, [mainActor], [mainActor.name])


Event.registerEvent("MamiDecap", func)
