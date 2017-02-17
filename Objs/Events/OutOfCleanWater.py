from Objs.Events.Event import Event

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.removeItem(state["items"]["Clean Water"])
    desc = mainActor.name + " ran out of "+state["items"]["Clean Water"].friendly+"."
    return (desc, [mainActor, state["items"]["Clean Water"]], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("OutOfCleanWater", func)
