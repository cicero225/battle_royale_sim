
from Objs.Events.Event import Event

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    mainActor.permStatChange({'stability': -1,
                              'endurance': -1,
                              'loneliness': 1})
    desc = mainActor.name+' questions '+Event.parseGenderPossessive(mainActor)+' sanity.'
    return (desc, [mainActor], []) # Second entry is the contestants named in desc, in order. Third is anyone who died.

Event.registerEvent("QuestionsSanity", func)

