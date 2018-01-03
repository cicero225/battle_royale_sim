
from Objs.Events.Event import Event


def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.permStatChange({'stability': -1,
                              'endurance': -1,
                              'loneliness': 1})
    desc = mainActor.name + ' questions ' + \
        Event.parseGenderPossessive(mainActor) + ' sanity.'
    # Second entry is the contestants named in desc, in order. Third is anyone who died.
    return (desc, [mainActor], [])


Event.registerEvent("QuestionsSanity", func)
