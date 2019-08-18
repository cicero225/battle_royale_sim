"""Provides an object that handles the registration and deregistration of the callbacks for a given non-standard event,
providing convenient methods for common tasks.

Usage: Instantiate the object when needed, perform the necessary operations, and store in state["callbackStore"] (probably
under a key such as mainActor.name which will properly identify it). When the callbacks are no longer leader, delete from the
state. If a group of callbacks may be deleted under different circumstances, it is probably best to make two objects."""

from copy import copy
from functools import partial
import random
import warnings
from Objs.Contestants.Contestant import Contestant
from Objs.Utilities.ArenaUtils import DictToOrderedDict


class IndividualEventHandler(object):
    # Regulating the participants in multi-participant events stresses the event model
    # and requires detailed tracking. Thie dict tracks who has been bound to what on global
    # basis. Subdict is assumed to be symmetric and consistent. All contestants stored by id.
    BOUND_PARTICIPANTS_DICT = {}  # Eventname: Actor: Other participants.

    def __init__(self, state):
        self.state = state
        # List of tuples, (callback list name where callback is stored, callback)
        self.callbackReferences = []

    def __del__(self):
        for toRemove in self.callbackReferences:
            try:
                self.state["callbacks"][toRemove[0]].remove(toRemove[1])
            except ValueError:
                pass
                #warnings.warn('IndividualEventHandler: Attempted to remove invalid callback '+str(toRemove[1])+'('+toRemove[1].eventName+') from '+toRemove[0])
        self.callbackReferences = []

    def registerEvent(self, locationListName, func, front=True):
        if front:
            self.state["callbacks"][locationListName].insert(0, func)
        else:
            self.state["callbacks"][locationListName].append(func)
        self.callbackReferences.append((locationListName, func))

    def setEventWeightForSingleContestant(self, eventName, contestantName, weight, state):
        def func(actor, origWeight, event):
            # if we're trying to set a weight to positive but it's the wrong phase
            if weight and "phase" in event.baseProps and state["curPhase"] not in event.baseProps["phase"]:
                return (origWeight, True)
            if event.name == eventName and actor.name == contestantName:
                # if weight is 0, we almost always want this to return False and block the event entirely
                return (weight, bool(weight))
            else:
                return (origWeight, True)

        # this anonymizes func, giving a new reference each time this is called
        def anonfunc(actor, origWeight, event): return func(
            actor, origWeight, event)
        anonfunc.eventName = eventName  # Notes on the functor for debug purposes
        anonfunc.contestantName = contestantName
        # This needs to be at beginning for proper processing
        self.registerEvent("modifyIndivActorWeights", anonfunc)
        return anonfunc  # Just in case it's needed by the calling function

    def bindRoleForContestantAndEvent(self, roleName, fixedRoleList, relevantActor, eventName, useOtherConstestantsIfNotAvailable=False):
        anonfunc = partial(self.fixedRoleCallback, roleName,
                           fixedRoleList, relevantActor, eventName, BOUND_PARTICIPANTS_DICT, useOtherConstestantsIfNotAvailable)
        anonfunc.eventName = eventName  # Notes on the functor for debug purposes
        anonfunc.relevantActor = relevantActor
        anonfunc.fixedRoleList = fixedRoleList
        self.registerEvent("overrideContestantEvent", anonfunc)
        
        if not isinstance(fixedRoleList, list):
            fixedRoleList = [fixedRoleList]
        new_group = set(x.id for x in fixedRoleList)
        # BOUND_PARTICIPANTS_DICT.setdefault(eventName, dict()).setdefault(relevantActor.id, set()).update(new_group)
        new_group.update(relevantActor.id)
        total_union = copy(new_group)
        for x in new_group:  # depth 1 is fine if we always do this.
            total_union.update(BOUND_PARTICIPANTS_DICT[eventName].setdefault(x, set()))
        for x in new_group:
            # Internally this will all be the same set.
            BOUND_PARTICIPANTS_DICT[eventName][x] = total_union
        
        # It must _also_ be checked that the people bound all still live. This has be done before the event is selected, to prevent the selection
        # of invalid events. Note that this is only necessary if useOtherConstestantsIfNotAvailable is False.
        anonfunc2 = None
        if not useOtherConstestantsIfNotAvailable:
            def func(actor, origWeight, event):  # Black magic
                if event.name == eventName and actor.name == relevantActor.name:
                    for person in fixedRoleList:
                        if not person.alive:
                            return (0, False)
                return (origWeight, True)

            # this anonymizes func, giving a new reference each time this is called
            def anonfunc2(actor, origWeight, event): return func(
                actor, origWeight, event)
            # This needs to be at beginning for proper processing
            self.registerEvent("modifyIndivActorWeights", anonfunc2, False)

        return anonfunc, anonfunc2  # Just in case it's needed by the calling function

    @staticmethod
    def fixedRoleCallback(roleName, fixedRoleList, relevantActor, eventName, bound_participants_dict, useOtherConstestantsIfNotAvailable, contestantKey, thisevent, state, participants, victims, sponsorsHere):
        # Avoiding eval here
        roleDict = DictToOrderedDict({"participants": participants,
                                      "victims": victims,
                                      "sponsors": sponsorsHere})
        if thisevent.name == eventName:
            this_participant_Dict = bound_participants_dict[eventName]
            if relevantActor.name == contestantKey:
                numRoles = len(roleDict[roleName])
                liveFixedRoleList = [x for x in fixedRoleList if x.alive]
                if len(liveFixedRoleList) < numRoles:  # Not enough people to fill the roleDict
                    if not useOtherConstestantsIfNotAvailable:
                        return False, True
                    newRolelist = random.sample(roleDict[roleName], numRoles - len(liveFixedRoleList))
                    # Have to clear the list BUT keep the reference
                    del roleDict[roleName][:]
                    roleDict[roleName].extend(newRolelist)
                    roleDict[roleName].extend(liveFixedRoleList)                
                else:
                    # Have to clear the list BUT keep the reference
                    del roleDict[roleName][:]
                    roleDict[roleName].extend(random.sample(liveFixedRoleList, numRoles))
            if roleName == "participants" :
                # We need to parse the participants list and see if some participants must
                # be added. In the worst case reset event.
                for participant in participants:
                    possible_list = this_participant_Dict.get(participant.id)
                    if possible_list is not None:
                        if not useOtherConstestantsIfNotAvailable:
                            return False, True
                            
        return True, False

    def banEventForSingleContestant(self, eventName, contestantName, state):
        self.setEventWeightForSingleContestant(
            eventName, contestantName, 0, state)

    def banMurderEventsAtoB(self, cannotKill, cannotBeVictim):
        def func(contestantKey, thisevent, state, participants, victims, sponsorsHere):
            if "murder" in thisevent.baseProps and thisevent.baseProps["murder"] and contestantKey == str(cannotKill):
                if cannotBeVictim in victims or (not victims) and cannotBeVictim in participants:
                    return False, True
            return True, False

        def anonfunc(contestantKey, thisevent, state, participants, victims, sponsorsHere): return func(contestantKey, thisevent,
                                                                                                        state, participants, victims, sponsorsHere)  # this anonymizes func, giving a new reference each time this is called
        anonfunc.cannotKill = cannotKill  # Notes on the functor for debug purposes
        anonfunc.cannotBeVictim = cannotBeVictim
        # This needs to be at beginning for proper processing
        self.registerEvent("overrideContestantEvent", anonfunc)
        return anonfunc  # Just in case it's needed by the calling function
