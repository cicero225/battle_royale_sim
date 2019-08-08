from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    victims[0].kill()
    desc = mainActor.name + ' killed ' + victims[0].name + "."
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, [mainActor, victims[0]], [victims[0].name])


Event.registerEvent("TestOneKill", func)
