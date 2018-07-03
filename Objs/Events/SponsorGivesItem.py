from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    options = sorted(list(set(state["items"].values(
    )) - set(x for x in mainActor.inventory if not x.stackable)), key=lambda x: str(x))
    if not options:
        return None  # Pick a different event
    gift = random.choice(options)
    mainActor.addItem(gift)
    # To get the actual item name, we need to get the name of the item INSTANCE
    friendlyName = mainActor.hasThing(gift)[0].friendly
    state["allRelationships"].IncreaseFriendLevel(
        mainActor, sponsors[0], random.randint(1, 2))
    choice = random.randint(0, 1)
    if choice:
        desc = sponsors[0].name + ' gave ' + \
            friendlyName + ' to ' + mainActor.name + "."
        return (desc, [sponsors[0], gift, mainActor], [])
    else:
        desc = 'An unknown sponsor gave ' + friendlyName + ' to ' + mainActor.name + "."
        # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
        return (desc, [gift, mainActor], [])


Event.registerEvent("SponsorGivesItem", func)
