from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.addItem(state["items"]["Clean Water"], isNew=True)
    desc = mainActor.name + " found a river with " + \
        state["items"]["Clean Water"].friendly + ", and collected some."
    # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    return (desc, [mainActor, state["items"]["Clean Water"]], [])


Event.registerEvent("FindRiverCleanWater", func)
