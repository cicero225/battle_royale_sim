from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = mainActor.name + ' hunted for others to kill.'
    # Second entry is the contestants named in desc, in order. Third is anyone who died.
    return (desc, [mainActor], [])


Event.registerEvent("HuntsForOthers", func)
