from Objs.Events.Event import Event

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):                            
    if mainActor.stats["stability"] < 4:
        desc = mainActor.name+' sleeps fitfully, disturbed by the recent events.'
        mainActor.permStatChange({'stability': +0.5})
    else:
        desc = mainActor.name+' sleeps, preparing for another long day tomorrow.'
        mainActor.permStatChange({'stability': +1})
    return (desc, [mainActor], []) # Second entry is the contestants named in desc, in order. Third is anyone who died.

Event.registerEvent("Sleep", func)

