"""Useful object for arranging relationship-related helper functions, etc."""

import itertools
import collections
from functools import partial

class Relationship(object):

    def __init__(self, contestants, sponsors, settings):
        self.settings = settings
        self.friendships = collections.defaultdict(partial(collections.defaultdict,int)) #Storing it like this is more memory-intensive than storing pointers in the contestants, but globally faster.
        self.loveships = collections.defaultdict(partial(collections.defaultdict,int)) # In this case, the use of these dictionaries is very immunzied from json typos
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
        if "mainFriendEffect" in event.baseProps and event.baseProps["mainFriendEffect"]:
            negOrPos = 1 if event.baseProps["mainNeededFriendLevel"]["relation"] else -1
            for friendLevel in self.friendships[actor.name].values():
                if negOrPos*friendLevel >= event.baseProps["mainNeededFriendLevel"]["value"]:
                    baseEventActorWeight *= (1+self.settings["relationInfluence"])**event.baseProps["mainFriendEffect"]
                    break
        if "mainLoveEffect" in event.baseProps and event.baseProps["mainLoveEffect"]:
            negOrPos = 1 if event.baseProps["mainNeededLoveLevel"]["relation"] else -1
            for loveLevel in self.loveships[actor.name].values():
                if negOrPos*loveLevel >= event.baseProps["mainNeededLoveLevel"]["value"]:
                    baseEventActorWeight *= (1+self.settings["relationInfluence"])**event.baseProps["mainLoveEffect"]
                    break
        return (baseEventActorWeight, True)
     
    def relationsRoleWeightCallback(self, roleName, actor, role, baseEventRoleWeight, event): # the string roleName should be bound when this callback is registered
        assert not (("mutual" in event.baseProps and event.baseProps["mutual"]) and ("reverse" in event.baseProps and event.baseProps["reverse"]))
        if "friendRequired"+roleName in event.baseProps and event.baseProps["friendRequired"+roleName]: 
            negOrPos = 1 if event.baseProps["neededFriendLevel"+roleName]["relation"] else -1
            if not ("reverse" in event.baseProps and event.baseProps["reverse"]):
                if negOrPos*self.friendships[actor.name][role.name]<negOrPos*event.baseProps["neededFriendLevel"+roleName]["value"]:
                    return (0, False)
            if ("mutual" in event.baseProps and event.baseProps["mutual"]) or ("reverse" in event.baseProps and event.baseProps["reverse"]):
                if negOrPos*self.friendships[role.name][actor.name]<negOrPos*event.baseProps["neededFriendLevel"+roleName]["value"]:
                    return (0, False)
        if "loveRequired"+roleName in event.baseProps and event.baseProps["loveRequired"+roleName]:
            negOrPos = 1 if event.baseProps["neededLoveLevel"+roleName]["relation"] else -1
            if not ("reverse" in event.baseProps and event.baseProps["reverse"]):
                if negOrPos*self.loveships[actor.name][role.name]<negOrPos*event.baseProps["neededLoveLevel"+roleName]["value"]:
                    return (0, False)
            if ("mutual" in event.baseProps and event.baseProps["mutual"]) or ("reverse" in event.baseProps and event.baseProps["reverse"]):
                if negOrPos*self.loveships[role.name][actor.name]<negOrPos*event.baseProps["neededLoveLevel"+roleName]["value"]:
                    return (0, False)
        if "reverse" in event.baseProps and event.baseProps["reverse"]:
            friendlevel = self.friendships[role.name][actor.name]
            lovelevel = self.loveships[role.name][actor.name]
        else:
            friendlevel = self.friendships[actor.name][role.name]
            lovelevel = self.loveships[actor.name][role.name]
            if "mutual" in event.baseProps and event.baseProps["mutual"]:
                friendlevel = (friendlevel+self.friendships[role.name][actor.name])/2
                lovelevel = (lovelevel+self.loveships[role.name][actor.name])/2
        return(baseEventRoleWeight*
              (1+self.settings["relationInfluence"])**(friendlevel*event.baseProps["friendEffect"+roleName])*
              (1+self.settings["relationInfluence"])**(lovelevel*event.baseProps["loveEffect"+roleName]),
              True)