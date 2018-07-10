from Objs.Events.Event import Event
import collections
import random
from Objs.Utilities.ArenaUtils import DictToOrderedDict


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = str(mainActor) + ' built an explosive trap to kill other contestants with.'

    state["events"]["DiesFromExplosiveTrap"].eventStore.setdefault("trapCounter", 0)
    state["events"]["DiesFromExplosiveTrap"].eventStore["trapCounter"] += 1
    state["events"]["DiesFromExplosiveTrap"].eventStore.setdefault("trapMakerCounter", collections.OrderedDict())
    state["events"]["DiesFromExplosiveTrap"].eventStore["trapMakerCounter"].setdefault(
        str(mainActor), 0)
    state["events"]["DiesFromExplosiveTrap"].eventStore["trapMakerCounter"][str(
        mainActor)] += 1

    return (desc, [mainActor], [])


Event.registerEvent("SetExplosiveTrap", func)
