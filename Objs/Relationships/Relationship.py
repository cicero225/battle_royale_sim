"""Useful object for arranging relationship-related helper functions, etc."""

import itertools

class Relationship(object):

    def __init__(self, contestants, sponsors, settings):
        self.settings = settings
        self.friendships = {} #Storing it like this is more memory-intensive than storing pointers in the contestants, but globally faster.
        self.loveships = {}
        mergedpeople = list(contestants.keys()) + list(sponsors.keys()) #Or I could write a generator to combine the iterators, but I'll just spend the memory for now
        for contestant in  mergedpeople:
            self.friendships[contestant]={}
            self.loveships[contestant]={}
        for contestant1, contestant2 in itertools.combinations(mergedpeople, 2):
            self.friendships[contestant1][contestant2] = 0  # Relationships can be bidirectional. Dict keys must be immutable and tuples are only immutable if all their entries are.
            self.friendships[contestant2][contestant1] = 0
            self.loveships[contestant1][contestant2] = 0
            self.loveships[contestant2][contestant1] = 0
            
    def IncreaseFriendLevel(self, name1, name2, change):
        self.friendships[name1][name2] = max(min(self.friendships[name1][name2]+change, 5), -5)
        
    def IncreaseLoveLevel(self, name1, name2, change):
        self.loveships[name1][name2] = max(min(self.loveships[name1][name2]+change, 5), -5)
        
    def relationsMainWeightCallback(self, actor, baseEventActorWeight, event):
        if event.baseProps["mainFriendEffect"]:
            negOrPos = 1 if event.baseProps["mainNeededFriendLevel"]["relation"] else -1
            for friendLevel in self.friendships[actor.name].values():
                if negOrPos*friendLevel >= event.baseProps["mainNeededFriendLevel"]["value"]:
                    baseEventActorWeight *= (1+self.settings["relationInfluence"])**event.baseProps["mainFriendEffect"]
                    break
        if event.baseProps["mainLoveEffect"]:
            negOrPos = 1 if event.baseProps["mainNeededLoveLevel"]["relation"] else -1
            for loveLevel in self.loveships[actor.name].values():
                if negOrPos*loveLevel >= event.baseProps["mainNeededLoveLevel"]["value"]:
                    baseEventActorWeight *= (1+self.settings["relationInfluence"])**event.baseProps["mainLoveEffect"]
                    break
        return (baseEventActorWeight, True)

    
    def relationsParticipantWeightCallback(self, actor, participant, baseEventParticipantWeight, event):
        if "friendRequired" in event.baseProps and event.baseProps["friendRequired"]:
            negOrPos = 1 if event.baseProps["neededFriendLevel"]["relation"] else -1
            if negOrPos*self.friendships[actor.name][participant.name]<negOrPos*event.baseProps["neededFriendLevel"]["value"]:
                return (0, False)
            if "mutual" in event.baseProps and event.baseProps["mutual"]:
                if negOrPos*self.friendships[participant.name][actor.name]<negOrPos*event.baseProps["neededFriendLevel"]["value"]:
                    return (0, False)
        if "loveRequired" in event.baseProps and event.baseProps["loveRequired"]:
            negOrPos = 1 if event.baseProps["neededLoveLevel"]["relation"] else -1
            if negOrPos*self.loveships[actor.name][participant.name]<negOrPos*event.baseProps["neededLoveLevel"]["value"]:
                return (0, False)
            if "mutual" in event.baseProps and event.baseProps["mutual"]:
                if negOrPos*self.loveships[participant.name][actor.name]<negOrPos*event.baseProps["neededLoveLevel"]["value"]:
                    return (0, False)
        friendlevel = self.friendships[actor.name][participant.name]
        lovelevel = self.loveships[actor.name][participant.name]
        if "mutual" in event.baseProps and event.baseProps["mutual"]:
            friendlevel = (friendlevel+self.friendships[participant.name][actor.name])/2
            lovelevel = (lovelevel+self.loveships[participant.name][actor.name])/2
        return(baseEventParticipantWeight*
              (1+self.settings["relationInfluence"])**(friendlevel*event.baseProps["friendEffect"])*
              (1+self.settings["relationInfluence"])**(lovelevel*event.baseProps["loveEffect"]),
              True)
     
     
    def relationsVictimWeightCallback(self, actor, victim, baseEventVictimWeight, event):
        if "friendRequiredVictim" in event.baseProps and event.baseProps["friendRequiredVictim"]: 
            negOrPos = 1 if event.baseProps["neededFriendLevelVictim"]["relation"] else -1
            if negOrPos*self.friendships[actor.name][victim.name]<negOrPos*event.baseProps["neededFriendLevelVictim"]["value"]:
                return (0, False)
            if "mutual" in event.baseProps and event.baseProps["mutual"]:
                if negOrPos*self.friendships[victim.name][actor.name]<negOrPos*event.baseProps["neededFriendLevel"]["value"]:
                    return (0, False)
        if "loveRequiredVictim" in event.baseProps and event.baseProps["loveRequiredVictim"]:
            negOrPos = 1 if event.neededLoveLevelVictim["relation"] else -1
            if negOrPos*self.loveships[actor.name][victim.name]<negOrPos*event.baseProps["neededLoveLevelVictim"]["value"]:
                return (0, False)
            if "mutual" in event.baseProps and event.baseProps["mutual"]:
                if negOrPos*self.loveships[victim.name][actor.name]<negOrPos*event.baseProps["neededLoveLevel"]["value"]:
                    return (0, False)
        friendlevel = self.friendships[actor.name][victim.name]
        lovelevel = self.loveships[actor.name][victim.name]
        if "mutual" in event.baseProps and event.baseProps["mutual"]:
            friendlevel = (friendlevel+self.friendships[victim.name][actor.name])/2
            lovelevel = (lovelevel+self.loveships[victim.name][actor.name])/2
        return(baseEventVictimWeight*
              (1+self.settings["relationInfluence"])**(friendlevel*event.baseProps["friendEffectVictim"])*
              (1+self.settings["relationInfluence"])**(lovelevel*event.baseProps["loveEffectVictim"]),
              True)