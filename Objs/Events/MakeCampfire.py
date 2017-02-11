from __future__ import division

from Objs.Events.Event import Event
from ..Utilities.ArenaUtils import weightedDictRandom
import random
from collections import defaultdict

# Survivalism, etc. shouldn't be included in the event weights, because this is kind of a neutral event.

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    success = True
    self.eventStore.setdefault('turnRecord', defaultdict(lambda: -1))[mainActor.name] = state["turnNumber"][0] # It's okay to overwrite since we only care if it happened this turn
    if str(mainActor) not in self.eventStore or not self.eventStore[str(mainActor)]:
        # base is 50%. unless the character has already done it before in which case success is assured
        chanceSuccess = mainActor.stats["cleverness"]*0.02 + mainActor.stats["survivalism"]*0.05 + 0.5  # Yes this can overload past 1
        if random.random()>chanceSuccess:
            desc = str(mainActor) + ' tried to start a fire, but failed.'
            descList = [mainActor]
            mainActor.SetHypothermic(state["turnNumber"][0])
            return (desc, descList, [])
    
    desc = str(mainActor) + ' successfully started a fire.'
    mainActor.SetUnhypothermic()
    self.eventStore[str(mainActor)] = True
    
    # Unless character already has clean water, 50% chance this becomes a clean water event
    if state["items"]["Clean Water"] not in mainActor.inventory:
        if random.random()>0.5:
            desc += ' Using it, '+Event.parseGenderSubject(mainActor)+' was able to boil some Clean Water.'
            mainActor.addItem(state["items"]["Clean Water"])
            descList = [mainActor, state["items"]["Clean Water"]]
            return (desc, descList, [])
    
    # 50% chance here that nothing happens, unless it just ain't possible for something to happen (other participant must not have already done this event this turn)
    possibleFireSharers = [x for x in state["contestants"].values() if x.alive and not self.eventStore["turnRecord"][x.name]==state["turnNumber"][0]]
    if not possibleFireSharers or random.random()>0.5: 
        desc += ' '+Event.parseGenderSubject(mainActor)+' was able to spend the night in comfort.'
        descList = [mainActor]
        return (desc, descList, [])
        
    # If someone finds them. Roll random contestant.
    contestant = random.choice(possibleFireSharers)
    desc += ' '+contestant.name+' found the fire'
    descList = [mainActor, contestant]
    
    # Use friendship and the other person's aggression/ruthlessness to determine what happens
    # Do they invite them to fire? - certain above 1 friendship or love, more ambivalent from -2 to 0, no below. Ruthlessness factors in.
    if ((state["allRelationships"].friendships[str(mainActor)][str(contestant)]>0 and state["allRelationships"].loveships[str(mainActor)][str(contestant)]>0)
        or (state["allRelationships"].friendships[str(mainActor)][str(contestant)]>-3 and state["allRelationships"].loveships[str(mainActor)][str(contestant)]>-3
        and random.random()<((min(state["allRelationships"].friendships[str(mainActor)][str(contestant)], state["allRelationships"].loveships[str(mainActor)][str(contestant)])+3)/3-mainActor.stats["ruthlessness"]/15))):
        desc += ', and they agreed to share the fire together.'
        state["allRelationships"].IncreaseFriendLevel(mainActor, contestant, random.randint(0,1))
        state["allRelationships"].IncreaseLoveLevel(mainActor, contestant, random.randint(0,1))
        state["allRelationships"].IncreaseFriendLevel(contestant, mainActor, random.randint(1,3))
        state["allRelationships"].IncreaseLoveLevel(contestant, mainActor, random.randint(0,2))
        return (desc, descList, [])
    
    desc += ', but '+mainActor.name+' refused to let '+Event.parseGenderObject(contestant)+' share it.'
    
    # Does the other party decide to attack? Only if friendship and loveship<0
    if ((state["allRelationships"].friendships[str(contestant)][str(mainActor)]>0 and state["allRelationships"].loveships[str(contestant)][str(mainActor)]>0)
        or random.random()>(contestant.stats["aggression"]*2+contestant.stats["ruthlessness"])*abs(state["allRelationships"].friendships[str(contestant)][str(mainActor)]+2*state["allRelationships"].loveships[str(contestant)][str(mainActor)])/450):
        desc += ' After a moment, '+contestant.name+' left.'
        # If guy leaving hasn't successfully started a fire yet, hypothermia.
        if str(contestant) not in self.eventStore or not self.eventStore[str(contestant)]:
            contestant.SetHypothermic(state["turnNumber"][0])
        return (desc, descList, [])
    
    desc += ' After a moment, '+contestant.name+' attacked. A fight started, '
    (fightDesc, fightDescList, fightDeadList) = Event.fight(descList, state["allRelationships"], state["settings"])
    # Special: if only one loser, 33% chance the loser escapes injured instead, losing loot.
    if len(fightDeadList)==1 and random.random()<0.33:
        # revive the loser
        fightDeadList[0].alive = True
        fightDeadList[0].SetInjured()
        if fightDeadList[0]==mainActor:
            desc += ' and '+mainActor.name+' was injured and forced to flee.'
            if fightDescList:
                desc += Event.parseGenderSubject(mainActor)+' left behind '+Event.englishList(fightDescList)+'.'
        else:
            desc += ' but '+contestant.name+' was injured and forced to flee.'
            if fightDescList:
                desc += Event.parseGenderSubject(contestant)+' left behind '+Event.englishList(fightDescList)+'.'
        descList.extend(fightDescList)
        return (desc, descList, [])
        
    # If nobody was hurt, they just give up and use the fire together.
    if not fightDeadList:
        desc += ' but in the end both sides got tired and gave up, agreeing to use the fire together for one night. Neither side slept well.'
        return (desc, descList, [])
    
    desc += fightDesc
    descList += fightDescList
    return (desc, descList, [x.name for x in fightDeadList])
    
Event.registerEvent("MakeCampfire", func)
