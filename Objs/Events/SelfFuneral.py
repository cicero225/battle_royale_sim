
from Objs.Events.Event import Event
import random

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    alt = random.randint(1,2)
    if alt == 1:
        desc = mainActor.name+' dug a grave and held an elaborate funeral ceremony for '+Event.parseGenderReflexive(mainActor)+', '
    else:
        desc = mainActor.name+" attempted to hang " +Event.parseGenderReflexive(mainActor)+ " with a makeshift noose, "
    potentialRescuers = [x for x in state['contestants'].values() if (x.alive and x != mainActor and (state['allRelationships'].friendships[x.name][mainActor.name]>=3 or state['allRelationships'].loveships[x.name][mainActor.name]>=2))]
    random.shuffle(potentialRescuers)
    for rescuer in potentialRescuers:
        if random.random()<0.25:
            trueRescuer = rescuer
            break
    else:
        if alt == 1:
            desc += 'before burying '+Event.parseGenderReflexive(mainActor)+' alive.'
        else:
            desc += "choking " +Event.parseGenderReflexive(mainActor)+ " in a long, arduous experience."
        mainActor.alive = False
        return desc, [mainActor], [mainActor.name]
    if alt == 1:
        desc += 'before trying to bury '+Event.parseGenderReflexive(mainActor)+' alive. However, '+trueRescuer.name+' was able to stop '+Event.parseGenderObject(mainActor)+' in time.'
    else:
        desc += "but " +trueRescuer.name+ " was able to stop " +Event.parseGenderObject(mainActor)+ " in time."
    state['allRelationships'].IncreaseFriendLevel(mainActor, trueRescuer, 3)
    state['allRelationships'].IncreaseLoveLevel(mainActor, trueRescuer, random.randint(1,3))
    mainActor.permStatChange({'stability': 2,
                              'endurance': 2,
                              'loyalty': 1})
    return desc, [mainActor, trueRescuer], []

Event.registerEvent("SelfFuneral", func)
