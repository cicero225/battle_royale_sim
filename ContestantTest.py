## OUTDATED DO NOT USE

from __future__ import division # In case of Python 2+. The Python 3 implementation is way less dumb.

from Contestants.Contestant import Contestant, contestantIndivActorCallback, contestantIndivActorWithParticipantsCallback, contestantIndivActorWithVictimsCallback
from Events import *  # necessary for some tests. This kind of mixing in tests is bad, but otherwise it's a huge amount of work to fake these classes.
from Items.Item import Item

import ArenaUtils
import collections

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
        self.inDict = collections.OrderedDict()
        self.inDict["imageFile"] = "dummy.jpg"
        self.inDict["stats"] = {"wideness": 6, "suffering": 4, "potential": 10, "english": 0}
        self.contestant = Contestant(self.name, self.inDict, self.settings)
        # TODO: Make a dummy event set so you can test InitializeEventModifiers
        self.contestant.events = collections.OrderedDict()
        self.contestant.callFlags = collections.OrderedDict()
    
    def refreshTest(self):
        self.contestant = Contestant(self.name, self.inDict, self.settings)
        self.callFlags = collections.OrderedDict()
    
    def testStatRandomizer(self):
        #Not super-stringent, but doesn't have to be.
        for key, value in self.contestant.stats.items():
            assert value>=0 and value<=10
            assert abs(value - self.contestant.originalStats[key])<=self.settings["traitRandomness"]
           
    def testRandomContestant(self):
        Contestant.makeRandomContestant("Rando", "dummy.jpg", self.contestant.stats, self.settings)
        
    def testItemHandling(self):
        dummyItemDict = {"statChanges": 
                            {"endurance": 1,
                             "survivalism": 1
                             },
                        "eventMultipliers":
                            {"blank": 0.0
                            },
                        "eventAdditions":
                            {"blank": 0.0
                            },
                        "eventsDisabled": {
                            "dysentary": True,
                            "giftwater": True
                            }
                        }
        dummyItem = Item("dummyItem", dummyItemDict, self.settings)
        def func1(x):
            x.callFlags["applyObjectStatChanges"]=1
        dummyItem.applyObjectStatChanges = func1
        def func2(x):
            x.callFlags["onAcquisition"]=1
        dummyItem.onAcquisition = func2
        def func3(x):
            x.callFlags["onRemoval"]=1
        dummyItem.onRemoval = func3
        self.contestant.addItem(dummyItem)  # This is simple enough that for now I'm okay not testing the less likely to fail bits
        assert self.contestant.callFlags["applyObjectStatChanges"]==1
        assert self.contestant.callFlags["onAcquisition"]==1
        assert not self.contestant.addItem(dummyItem)  # will fail on adding twice
        # TODO: when dummy event set is made, test that EventModifiers are correct
        self.contestant.removeItem(dummyItem)
        assert self.contestant.callFlags["onRemoval"]==1
        assert not self.contestant.removeItem(dummyItem)  # Cannot remove twice...
        # TODO: when dummy event set is made, test that EventModifiers are correct
        self.refreshTest()

if __name__ == "__main__":
    # execute only if run as a script
    thisTest = ContestantTest()
    thisTest.testStatRandomizer()
    thisTest.testRandomContestant()
    thisTest.testItemHandling()