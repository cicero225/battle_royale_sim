
from Objs.Events.Event import Event
import random


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    options = sorted(set(str(x) for x in state["items"].values(
    )) - set(str(x) for x in mainActor.inventory if not x.stackable), key=lambda x: str(x))
    if not options:
        return None  # Pick a different event
    gift = random.choice(options)
    itemInstance = mainActor.addItem(gift, isNew=True, resetItemAllowed=True)
    # To get the actual item name, we need to get the name of the item INSTANCE
    friendlyName = itemInstance.friendly
    desc = mainActor.name + ' managed to successfully sneak in and grab ' + friendlyName
    return (desc, [mainActor, itemInstance], [])


Event.registerEvent("SuccessfulSneak", func)
