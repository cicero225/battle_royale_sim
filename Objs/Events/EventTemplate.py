from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = mainActor.name + ' did absolutely nothing.'
    # Second entry is the contestants named in desc, in order. Third is anyone who died. The fourth is optional, and lists anyone who should be blamed for the deaths involved. This MUST be a dict if used.
    # The 5th can be used to override the list of candidates "consumed" by this event and ineligible for further events, which defaults to mainActor + participants + victims
    # The last is a kludge, and indicates whether it is is okay for this event to end the game with no one left in the contestant pool (default False)
    return (desc, [mainActor], [], [], [], False)


Event.registerEvent("EventTemplate", func)
