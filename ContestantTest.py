

from __future__ import division # In case of Python 2+. The Python 3 implementation is way less dumb.

from Contestants.Contestant import Contestant, contestantIndivActorCallback, contestantIndivActorWithParticipantsCallback, contestantIndivActorWithVictimsCallback

import ArenaUtils

class ContestantTest(object):

    def __init__(self): # This incidentally tests the constructor, but will probably be useful for other things
        self.settings = {
                         "traitRandomness": 3,
                         "numContestants": 24, # Program should pad or randomly remove contestants as necessary
                         "eventRandomness": 0.5, # Percent range over which the base weights of events varies from json settings
                         "statInfluence": 0.3, # How much stats influence event weightings, calculated as (1+influence)^((stat-5)*eventInfluenceLevel)
                         "objectInfluence": 1, # How much objects in inventory affect events. The default 1 uses the base stats.
                         "relationInfluence": 0.3 # How much relationships affect event chance, calculated as (1+influence)^(relationship level*eventInfluenceLevel)
                        }
        self.name = "FakeContestant"
        self.inDict = {}
        self.inDict["imageFile"] = "dummy.jpg"
        self.inDict["stats"] = {"wideness": 6, "suffering": 4}
        self.contestant = Contestant(self.name, self.inDict, self.settings)
        

if __name__ == "__main__":
    # execute only if run as a script
    thisTest = ContestantTest()