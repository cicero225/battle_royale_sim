"""Useful object for arranging relationship-related helper functions, etc."""
from __future__ import division

import itertools
import collections
import math
import random
from functools import partial
from Objs.Utilities.ArenaUtils import inv_erf

class Relationship(object):

    def __init__(self, contestants, sponsors, settings):
        self.settings = settings
        self.contestants = contestants
        self.sponsors = sponsors
        self.friendships = collections.defaultdict(partial(collections.defaultdict,int)) #Storing it like this is more memory-intensive than storing pointers in the contestants, but globally faster.
        self.loveships = collections.defaultdict(partial(collections.defaultdict,int)) # In this case, the use of these dictionaries is very immunzied from json typos
        mergedpeople = list(contestants.keys()) + list(sponsors.keys()) #Or I could write a generator to combine the iterators, but I'll just spend the memory for now
        for contestant in  mergedpeople:
            self.friendships[contestant]={}
            self.loveships[contestant]={}
        desiredSD = 4/(inv_erf(1-2*settings["meanNumInitialRelationships"]/len(mergedpeople))*math.sqrt(2))  # we want to set SD such that "meanNumInitialRelationships" people end up beyond 4
        for contestant1, contestant2 in itertools.combinations(mergedpeople, 2):
            self.friendships[contestant1][contestant2] = min(max(random.gauss(0, desiredSD),-5),5)  # Relationships can be bidirectional. Dict keys must be immutable and tuples are only immutable if all their entries are.
            self.friendships[contestant2][contestant1] = self.friendships[contestant1][contestant2] # But start them off equal
            self.loveships[contestant1][contestant2] = min(max(random.gauss(0, desiredSD),-5),5)
            self.loveships[contestant2][contestant1] = self.loveships[contestant1][contestant2]
            
    def aliveOrSponsor(self, contestant):  # Convenience function for checking if contestant is valid/alive
        contestantKey = str(contestant)
        return ((contestantKey in self.sponsors) or self.contestants[contestantKey].alive)
            
    def processTraitEffect(self, event, actor, others):
        if "sponsorInfluence" not in event.baseProps:
            return
        def processSingleTrait(trait_name, sponsor):
            if trait_name in event.baseProps["sponsorInfluence"]:
                self.IncreaseFriendLevel(sponsor, actor, event.baseProps["sponsorInfluence"][trait_name]["value"])
                if "all" not in event.baseProps["sponsorInfluence"][trait_name] or event.baseProps["sponsorInfluence"][trait_name]["all"]:
                    for contestant in others:
                        self.IncreaseFriendLevel(sponsor, contestant, event.baseProps["sponsorInfluence"][trait_name]["value"])
        for sponsor in self.sponsors.values():
            processSingleTrait(sponsor.primary_trait, sponsor)
            processSingleTrait(sponsor.secondary_trait, sponsor)
    
    def decay(self, unused_state):
        # Only decay between alive contestants
        for contestant, contestantFriends in self.friendships.items():
            if not self.aliveOrSponsor(contestant):
                continue
            for contestant2 in contestantFriends:
                if not self.aliveOrSponsor(contestant2):
                    continue
                if contestantFriends[contestant2] > 0:
                    contestantFriends[contestant2] -= max(self.settings["relationshipDecay"], 0)
                if contestantFriends[contestant2] < 0:
                    contestantFriends[contestant2] += min(self.settings["relationshipDecay"], 0)
        for contestant, contestantLoves in self.loveships.items():
            if not self.aliveOrSponsor(contestant):
                continue
            for contestant2 in contestantLoves:
                if not self.aliveOrSponsor(contestant2):
                    continue
                if contestantLoves[contestant2] > 0:
                    contestantLoves[contestant2] -= max(self.settings["relationshipDecay"]*0.5, 0)
                if contestantLoves[contestant2] < 0:
                    contestantLoves[contestant2] += min(self.settings["relationshipDecay"]*0.5, 0)
    
    def propagateFriendshipChange(self, original, target, change): # For now, changes in friendship propagate to friendship, but changes in loveship do not propagate. Note that this propagates to sponsors!
        for person in list(self.contestants.values()) + list(self.sponsors.values()):
            if person.name == str(original) or person.name == str(target):
                continue
            self.IncreaseFriendLevel(person, target, change*(self.friendships[person.name][original.name] + 2*self.loveships[person.name][original.name])/5*self.settings["relationshipPropagation"] , False)
    
    def IncreaseFriendLevel(self, person1, person2, change, propagate=True):
        if propagate:
            self.propagateFriendshipChange(person1, person2, change)
        change *= random.uniform(1-self.settings["relationshipRandomizer"], 1+self.settings["relationshipRandomizer"])
        curLevel = self.friendships[person1.name][person2.name]
        if curLevel > 0:
            if change > 0:
                stat = 'friendliness'
            else:
                stat = 'loyalty'
        else:
            if change > 0:
                stat = 'forgiveness'
            else:
                stat = 'meanness'    
        change *= (1+self.settings['statFriendEffect'])**((person1.stats[stat]-5)/5)
        self.friendships[person1.name][person2.name] = max(min(curLevel+change, 5), -5)
        
    def IncreaseLoveLevel(self, person1, person2, change):
        change *= random.uniform(1-self.settings["relationshipRandomizer"], 1+self.settings["relationshipRandomizer"])
        curLevel = self.loveships[person1.name][person2.name]
        if curLevel > 0:
            if change > 0:
                stat = 'loneliness'
            else:
                stat = 'loyalty'
        else:
            if change > 0:
                stat = 'forgiveness'
            else:
                stat = 'meanness'    
        change *= (1+self.settings['statFriendEffect'])**((person1.stats[stat]-5)/5)
        self.loveships[person1.name][person2.name] = max(min(curLevel+change, 5), -5)
    
    def KillImpact(self, deadPerson):
        for person in list(self.contestants.values()):
            if str(person) == str(deadPerson):
                continue
            person.permStatChange({'stability': -self.settings["deathImpactOnStability"]*random.uniform(0.5, 1.5)/15*(max(0, self.friendships[str(person)][str(deadPerson)]) + 2*max(0, self.loveships[str(person)][str(deadPerson)]))})
    
    def groupFriendLevel(self, names):
        totSum = 0
        for x in names:
            for y in names:
                if x == y:
                    continue
                totSum += self.friendships[x][y]
        return totSum/(len(names)*len(names))
    
    def groupLoveLevel(self, names):
        totSum = 0
        for x in names:
            for y in names:
                if x == y:
                    continue
                totSum += self.loveships[x][y]
        return totSum/(len(names)*len(names))
        
    def groupCohesion(self, people): # this ends up being a value from -50 to 50
        names = [person.name for person in people]
        groupCohesion = sum([self.groupFriendLevel(names), 2*self.groupLoveLevel(names)])/3
        groupCohesion *= (sum(person.stats['loyalty'] for person in people) if groupCohesion>0 else
                               (10-sum(person.stats['forgiveness'] for person in people)))/len(people)
        return groupCohesion
    
    def relationsMainWeightCallback(self, actor, baseEventActorWeight, event):
        if "mainFriendEffect" in event.baseProps and event.baseProps["mainFriendEffect"]:
            negOrPos = 1 if event.baseProps["mainNeededFriendLevel"]["relation"] else -1
            for friendName, friendLevel in self.friendships[actor.name].items():
                if self.aliveOrSponsor(friendName) and negOrPos*friendLevel >= event.baseProps["mainNeededFriendLevel"]["value"]:
                    baseEventActorWeight *= (1+self.settings["relationInfluence"])**event.baseProps["mainFriendEffect"]
                    break
        if "mainLoveEffect" in event.baseProps and event.baseProps["mainLoveEffect"]:
            negOrPos = 1 if event.baseProps["mainNeededLoveLevel"]["relation"] else -1
            for loveName, loveLevel in self.loveships[actor.name].items():
                if self.aliveOrSponsor(loveName) and negOrPos*loveLevel >= event.baseProps["mainNeededLoveLevel"]["value"]:
                    baseEventActorWeight *= (1+self.settings["relationInfluence"])**event.baseProps["mainLoveEffect"]
                    break
        return (baseEventActorWeight, True)
     
    def relationsRoleWeightCallback(self, roleName, actor, role, baseEventRoleWeight, event): # the string roleName should be bound when this callback is registered
        roleNameLower = roleName.lower()
        assert("friendEffect"+roleName in event.baseProps or roleNameLower+"HasFriendEffect" in event.baseProps)
        assert("loveEffect"+roleName in event.baseProps or roleNameLower+"HasLoveEffect" in event.baseProps)        
        def checkIfRequirementMetHelper(relationshipDict, propertyName, forwardOrBackward):
            negOrPos = 1 if event.baseProps[propertyName]["relation"] else -1
            relValue = relationshipDict[actor.name][role.name] if forwardOrBackward else relationshipDict[role.name][actor.name]
            if negOrPos*relValue<negOrPos*event.baseProps[propertyName]["value"]:
                return False
            return True
        if "friendRequired"+roleName in event.baseProps and event.baseProps["friendRequired"+roleName]:
            if not checkIfRequirementMetHelper(self.friendships, "neededFriendLevel"+roleName, True):
                return (0, False)
        elif ("mutual" in event.baseProps and event.baseProps["mutual"]):
            if roleNameLower+"HasFriendRequired" in event.baseProps and event.baseProps[roleNameLower+"HasFriendRequired"]:
                if not checkIfRequirementMetHelper(self.friendships, roleNameLower+"HasNeededFriendLevel", True):
                    return (0, False)
        if roleNameLower+"HasFriendRequired" in event.baseProps and event.baseProps[roleNameLower+"HasFriendRequired"]:
            if not checkIfRequirementMetHelper(self.friendships, roleNameLower+"HasNeededFriendLevel", False):
                return (0, False)
        elif ("mutual" in event.baseProps and event.baseProps["mutual"]):
            if "friendRequired"+roleName in event.baseProps and event.baseProps["friendRequired"+roleName]:
                if not checkIfRequirementMetHelper(self.friendships, "neededFriendLevel"+roleName, False):
                    return (0, False)
        if "loveRequired"+roleName in event.baseProps and event.baseProps["loveRequired"+roleName]:
            if not checkIfRequirementMetHelper(self.loveships, "neededLoveLevel"+roleName, True):
                return (0, False)
        elif ("mutual" in event.baseProps and event.baseProps["mutual"]):
            if roleNameLower+"HasLoveRequired" in event.baseProps and event.baseProps[roleNameLower+"HasLoveRequired"]:
                if not checkIfRequirementMetHelper(self.loveships, roleNameLower+"HasNeededLoveLevel", True):
                    return (0, False)
        if roleNameLower+"HasLoveRequired" in event.baseProps and event.baseProps[roleNameLower+"HasLoveRequired"]:
            if not checkIfRequirementMetHelper(self.loveships, roleNameLower+"HasNeededLoveLevel", False):
                return (0, False)
        elif ("mutual" in event.baseProps and event.baseProps["mutual"]):
            if "loveRequired"+roleName in event.baseProps and event.baseProps["loveRequired"+roleName]:
                if not checkIfRequirementMetHelper(self.loveships, "neededLoveLevel"+roleName, False):
                    return (0, False)
        if "friendEffect"+roleName in event.baseProps:
            baseEventRoleWeight *= (1+self.settings["relationInfluence"])**(self.friendships[actor.name][role.name]*event.baseProps["friendEffect"+roleName])
        elif "mutual" in event.baseProps and event.baseProps["mutual"]:
            baseEventRoleWeight *= (1+self.settings["relationInfluence"])**(self.friendships[actor.name][role.name]*event.baseProps[roleNameLower+"HasFriendEffect"])
        if roleNameLower+"HasFriendEffect" in event.baseProps:
            baseEventRoleWeight *= (1+self.settings["relationInfluence"])**(self.friendships[role.name][actor.name]*event.baseProps[roleNameLower+"HasFriendEffect"])
        elif "mutual" in event.baseProps and event.baseProps["mutual"]:
            baseEventRoleWeight *= (1+self.settings["relationInfluence"])**(self.friendships[role.name][actor.name]*event.baseProps["friendEffect"+roleName])
        if "loveEffect"+roleName in event.baseProps:
            baseEventRoleWeight *= (1+self.settings["relationInfluence"])**(self.loveships[actor.name][role.name]*event.baseProps["loveEffect"+roleName])
        elif "mutual" in event.baseProps and event.baseProps["mutual"]:
            baseEventRoleWeight *= (1+self.settings["relationInfluence"])**(self.loveships[actor.name][role.name]*event.baseProps[roleNameLower+"HasLoveEffect"])
        if roleNameLower+"HasLoveEffect" in event.baseProps:
            baseEventRoleWeight *= (1+self.settings["relationInfluence"])**(self.loveships[role.name][actor.name]*event.baseProps[roleNameLower+"HasLoveEffect"])
        elif "mutual" in event.baseProps and event.baseProps["mutual"]:
            baseEventRoleWeight *= (1+self.settings["relationInfluence"])**(self.loveships[role.name][actor.name]*event.baseProps["loveEffect"+roleName])
        return (baseEventRoleWeight, True)
              
    def reprocessParticipantWeightsForVictims(self, possibleParticipantEventWeights, victims, event):
        possibleParticipantWeights = possibleParticipantEventWeights[event.name]
        for participantName, weight in possibleParticipantWeights.items():
            if not weight:
                continue
            for victim in victims:
                if "participantFriendRequiredVictim" in event.baseProps and event.baseProps["participantFriendRequiredVictim"]: 
                    negOrPos = 1 if event.baseProps["participantNeededFriendLevelVictim"]["relation"] else -1
                    if negOrPos*self.friendships[participantName][str(victim)]<negOrPos*event.baseProps["participantNeededFriendLevelVictim"]["value"]:
                        possibleParticipantWeights[participantName] = 0
                        break
                if "participantLoveRequiredVictim" in event.baseProps and event.baseProps["participantLoveRequiredVictim"]:
                    negOrPos = 1 if event.baseProps["participantNeededLoveLevelVictim"]["relation"] else -1
                    if negOrPos*self.loveships[participantName][str(victim)]<negOrPos*event.baseProps["participantNeededLoveLevelVictim"]["value"]:
                        possibleParticipantWeights[participantName] = 0
                        break
                friendlevel = self.friendships[participantName][str(victim)]
                lovelevel = self.loveships[participantName][str(victim)]
                possibleParticipantWeights[participantName] *= (
                      (1+self.settings["relationInfluence"])**(friendlevel*event.baseProps["participantFriendEffectVictim"] if "participantFriendEffectVictim" in event.baseProps else 1)*
                      (1+self.settings["relationInfluence"])**(lovelevel*event.baseProps["participantLoveEffectVictim"] if "participantLoveEffectVictim" in event.baseProps else 1))