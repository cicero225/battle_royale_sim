
from Objs.Events.Event import Event
import random

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = str(mainActor) + " offered to cook for " + str(participants[0]) + ", who gladly accepted."
    descList = [mainActor, participants[0]]
    
    # Roll for failure to actually poison
    notFailure = (participants[0].stats["cleverness"] + participants[0].stats["survivalism"])/15
    if random.random() > notFailure:
        desc += " However, " + str(mainActor) + " tried to secretly poison the dish, but failed, using the wrong mushrooms. The dish was delicious."
        state["allRelationships"].IncreaseFriendLevel(participants[0], mainActor, random.randint(1,3))
        state["allRelationships"].IncreaseLoveLevel(participants[0], mainActor, random.randint(0,2))
        return (desc, descList, [])
    
    desc += " However, " + str(mainActor) + " tried to secretly poison the dish! "
    
    # Roll for participant realizing what's going on
    detection = (participants[0].stats["cleverness"] + participants[0].stats["survivalism"])/30
    
    if random.random() < detection:
        # Participant realizes what's going on
        desc += str(participants[0]) + " caught " + Event.parseGenderObject(mainActor) + " in the act and attacked!"
        (fightDesc, fightDescList, fightDeadList) = Event.fight(descList, state["allRelationships"], state["settings"])
        # Special: if only one loser, 33% chance the loser escapes injured instead, losing loot.
        if len(fightDeadList)==1 and random.random()<0.33:
            # revive the loser
            fightDeadList[0].alive = True
            fightDeadList[0].SetInjured()
            if fightDeadList[0]==mainActor:
                desc += ' In the end, '+mainActor.name+' was injured and forced to flee.'
                if fightDescList:
                    desc += ' '+Event.parseGenderSubject(mainActor).capitalize()+' left behind '+Event.englishList(fightDescList)+'.'
            else:
                desc += ' In the end, however, '+participants[0].name+' was injured and forced to flee.'
                if fightDescList:
                    desc += ' '+Event.parseGenderSubject(participants[0]).capitalize()+' left behind '+Event.englishList(fightDescList)+'.'
            descList.extend(fightDescList)
            return (desc, descList, [])
        
        if not fightDeadList:
            desc += ' The fight was a draw, and the two sides departed, friends no more.'
            return (desc, descList, [])
        desc += " " + fightDesc[4:]
        descList += fightDescList
        return (desc, descList, [x.name for x in fightDeadList])
        
    else:
        desc += str(participants[0]) + " ate the meal, blissfully unaware, before falling over dead."
        participants[0].alive = False
    
    return (desc, descList, [str(participants[0])]) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.
    
Event.registerEvent("ACooksForBButPoison", func)