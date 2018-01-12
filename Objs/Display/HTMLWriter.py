from .LegacyWriter import LegacyWriter
from Objs.Events.Event import Event

import copy
import collections
import os

class HTMLWriter(object):
    def __init__(self):
        self.phaseWriter = None
        self.dayNumber = 0
        self.phase = None

    def newDay(self, day):
        self.dayNumber = day
        
    def newPhase(self, phase, phaseNameTemplate, statuses):
        self.phase = phase
        self.phaseWriter = LegacyWriter(statuses)
        self.phaseWriter.addTitle(phaseNameTemplate.replace('#', str(self.dayNumber)))

    def addEvent(self, desc, descContestants, state=None, preEventInjuries=None):
        self.phaseWriter.addEvent(desc, descContestants, state, preEventInjuries)
        
    def addBigLine(self, line):
        self.phaseWriter.addBigLine(line)

    def endPhase(self, state):
        filepath = self.filename("Phase " + self.phase)
        self.renderAndWrite(filepath, self.phaseWriter, state)
        self.writeDailyReports(state)

    def renderAndWrite(self, filepath, writer, state):
        with open(filepath, 'w') as target:
            for line in writer.render(state):
                target.write(line)

    def filename(self, topic):
        return os.path.join("Assets", str(self.dayNumber) + " " + topic + ".html")

    def bare_filename(self, topic):
        return os.path.join("Assets", topic + ".html")

    def writeStartupReports(self, state):
        self.relationshipReport(state)
        self.sponsorTraitReport(state)

    def writeDailyReports(self, state):
        self.killReport(state)
        self.itemsReport(state)
        self.statusReport(state)
        self.relationshipReport(state)

    def writeFinalReports(self, state):
        self.relationshipReport(state)

    def killReport(self, state):
        # TODO: look up how html tables work when you have internet... And make this include everyone (not just successful killers)
        from Objs.Events.Event import Event
        killWriter = LegacyWriter(state["statuses"])
        killWriter.addTitle("Day " + str(state["turnNumber"][0]) + " Kills")
        for contestant, kills in state["callbackStore"]["killCounter"].items():
            desc = 'Kills: ' + str(len(kills)) + '<br/>' + Event.englishList(kills, False)
            descContestant = state["contestants"][contestant]
            if not descContestant.alive:
                desc = '(DEAD) ' + desc
            killWriter.addEvent(desc, [descContestant])
        self.renderAndWrite(self.filename("Kills"), killWriter, state)
        return False

    def itemsReport(self, state):
        self.inventoryReport("Items", "inventory", state)

    def statusReport(self, state):
        self.inventoryReport("Statuses", "statuses", state)

    def inventoryReport(self, filename, inventory_attr_name, state):
        Writer = LegacyWriter(state["statuses"])
        Writer.addTitle(
            "Day " + str(state["turnNumber"][0]) + " " + filename + " Accumulated")
        for contestant in state["contestants"].values():
            if not contestant.alive or not getattr(contestant, inventory_attr_name):
                continue
            eventLine = str(contestant) + ": " + \
                Event.englishList(getattr(contestant, inventory_attr_name))
            Writer.addEvent(eventLine, [contestant] + getattr(contestant, inventory_attr_name))
        self.renderAndWrite(self.filename(filename), Writer, state)

    def sponsorTraitReport(self, state):
        sponsorWriter = LegacyWriter(state["statuses"])
        sponsorWriter.addTitle("Sponsor Traits")
        for sponsor in state["sponsors"].values():
            sponsorWriter.addEvent("Primary Trait: " + sponsor.primary_trait +
                                   "<br> Secondary Trait: " + sponsor.secondary_trait, [sponsor])
        self.renderAndWrite(self.bare_filename("Sponsor Traits"), sponsorWriter, state)

    def relationshipReport(self, state):
        relationships = state["allRelationships"]
        firstTurn = ("relationshipLastTurn" not in state["callbackStore"])
        if not firstTurn:
            oldRelationshipsFriendships = state["callbackStore"]["relationshipLastTurn"]["friendships"]
            oldRelationshipsLoveships = state["callbackStore"]["relationshipLastTurn"]["loveships"]
        state["callbackStore"]["relationshipLastTurn"] = collections.OrderedDict()
        state["callbackStore"]["relationshipLastTurn"]["friendships"] = copy.deepcopy(
            relationships.friendships)
        state["callbackStore"]["relationshipLastTurn"]["loveships"] = copy.deepcopy(
            relationships.loveships)

        friendWriter = LegacyWriter(state["statuses"])
        friendWriter.addTitle(
            "Day " + str(state["turnNumber"][0]) + " Friendships")
        loveWriter = LegacyWriter(state["statuses"])
        loveWriter.addTitle("Day " + str(state["turnNumber"][0]) + " Romances")
        # A hack to get around importing Events
        anyEvent = next(iter(state["events"].values()))
        for person in list(state["contestants"].values()) + list(state["sponsors"].values()):
            if not person.alive:
                continue
            friendLine = str(person)
            friendList = []
            lostFriendList = []
            enemyList = []
            lostEnemyList = []
            liveFriends = {x: y for x, y in relationships.friendships[str(person)].items(
            ) if x in state["contestants"] and state["contestants"][x].alive}
            liveFriends.update({x: y for x, y in relationships.friendships[str(
                person)].items() if x in state["sponsors"]})
            sortFriends = collections.OrderedDict()
            for x in sorted(liveFriends, key=liveFriends.get, reverse=True):
                sortFriends[x] = liveFriends[x]
            for key, value in sortFriends.items():
                if value >= 4:
                    writeString = key
                    if not firstTurn:
                        if oldRelationshipsFriendships[str(person)][key] < 4:
                            writeString += ' (New!) '
                    if relationships.friendships[key][str(person)] >= 4:
                        friendList.append(writeString)
                    else:
                        friendList.append(writeString + ' (Not Mutual)')
                else:
                    if not firstTurn:
                        if oldRelationshipsFriendships[str(person)][key] >= 4:
                            tempString = key
                            if oldRelationshipsFriendships[str(person)][key] < 4:
                                tempString += ' (Not Mutual)'
                            lostFriendList.append(tempString)
                if value <= -4:
                    writeString = key
                    if not firstTurn:
                        if oldRelationshipsFriendships[str(person)][key] > -4:
                            writeString += ' (New!) '
                    if relationships.friendships[key][str(person)] <= -4:
                        enemyList.append(writeString)
                    else:
                        enemyList.append(writeString + ' (Not Mutual)')
                else:
                    if not firstTurn:
                        if oldRelationshipsFriendships[str(person)][key] <= -4:
                            tempString = key
                            if oldRelationshipsFriendships[key][str(person)] > -4:
                                tempString += ' (Not Mutual)'
                            lostEnemyList.append(tempString)
            if friendList:
                friendLine += "<br> Friend: "
                friendLine += anyEvent.englishList(friendList, False)
            if lostFriendList:
                friendLine += "<br> No Longer Friends: "
                friendLine += anyEvent.englishList(lostFriendList, False)
            if enemyList:
                friendLine += "<br> Enemies: "
                friendLine += anyEvent.englishList(enemyList, False)
            if lostEnemyList:
                friendLine += "<br> No Longer Enemies: "
                friendLine += anyEvent.englishList(lostEnemyList, False)
            if friendList or lostFriendList:
                friendWriter.addEvent(friendLine, [person])

            loveLine = str(person)
            loveList = []
            lostLoveList = []
            loveEnemyList = []
            lostLoveEnemyList = []
            liveLoves = {x: y for x, y in relationships.loveships[str(person)].items(
            ) if x in state["contestants"] and state["contestants"][x].alive}
            liveLoves.update({x: y for x, y in relationships.loveships[str(
                person)].items() if x in state["sponsors"]})
            sortLoves = collections.OrderedDict()
            for x in sorted(liveLoves, key=liveLoves.get, reverse=True):
                sortLoves[x] = liveLoves[x]
            for key, value in sortLoves.items():
                if value >= 4:
                    writeString = key
                    if not firstTurn:
                        if oldRelationshipsLoveships[str(person)][key] < 4:
                            writeString += ' (New!) '
                    if relationships.loveships[key][str(person)] >= 4:
                        loveList.append(writeString)
                    else:
                        loveList.append(writeString + ' (Not Mutual)')
                else:
                    if not firstTurn:
                        if oldRelationshipsLoveships[str(person)][key] >= 4:
                            tempString = key
                            if oldRelationshipsLoveships[key][str(person)] < 4:
                                tempString += ' (Not Mutual)'
                            lostLoveList.append(tempString)
                if value <= -4:
                    writeString = key
                    if not firstTurn:
                        if oldRelationshipsLoveships[str(person)][key] > -4:
                            writeString += ' (New!) '
                    if relationships.loveships[key][str(person)] <= -4:
                        loveEnemyList.append(writeString)
                    else:
                        loveEnemyList.append(writeString + ' (Not Mutual)')
                else:
                    if not firstTurn:
                        if oldRelationshipsLoveships[str(person)][key] <= -4:
                            tempString = key
                            if oldRelationshipsLoveships[key][str(person)] > -4:
                                tempString += ' (Not Mutual)'
                            lostLoveEnemyList.append(key)
            if loveList:
                loveLine += "<br> Romances: "
                loveLine += anyEvent.englishList(loveList, False)
            if lostLoveList:
                loveLine += "<br> No Longer Lovers: "
                loveLine += anyEvent.englishList(lostLoveList, False)
            if loveEnemyList:
                loveLine += "<br> Romantic Enemies: "
                loveLine += anyEvent.englishList(loveEnemyList, False)
            if lostLoveEnemyList:
                loveLine += "<br> No Longer Romantic Enemies: "
                loveLine += anyEvent.englishList(lostLoveEnemyList, False)

            if loveList or lostLoveList:
                loveWriter.addEvent(loveLine, [person])

        self.renderAndWrite(self.filename("Friendships"), friendWriter, state)
        self.renderAndWrite(self.filename("Romances"), loveWriter, state)
