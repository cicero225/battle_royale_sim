# Unit-testing for the Util functions in ArenaUtils.

# In case of Python 2+. The Python 3 implementation is way less dumb.
from __future__ import division

import ArenaUtils
import io
import collections


class Dummy(object):  # This might have to be more elaborate for some of the other tests
    def __init__(self, name, inDict, settings):
        self.echoDict = inDict
        self.name = name


class ArenaUtilsTest(object):

    # This might have to be more elaborate for some of the other tests
    settings = collections.OrderedDict()

    def __init__(self):
        pass

    def TestLoadJSONIntoDictOfObjects(self):
        this_file = io.StringIO('''{"Ultimate Madoka": {"type": "divine","purity": true},
        "Akuma Homura": {"type": "devil","purity": false}}''')  # simulated file, keeping it enclosed in this method
        dummyDict = ArenaUtils.LoadJSONIntoDictOfObjects(
            this_file, self.settings, Dummy)
        assert "Ultimate Madoka" in dummyDict, "LoadJSONIntoDictOfObjectsTest failed, top-level key missing"
        assert "Akuma Homura" in dummyDict, "LoadJSONIntoDictOfObjectsTest failed, top-level key missing"
        assert dummyDict["Ultimate Madoka"].name == "Ultimate Madoka", "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert dummyDict["Ultimate Madoka"].echoDict["type"] == "divine", "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert dummyDict["Ultimate Madoka"].echoDict["purity"], "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert dummyDict["Akuma Homura"].name == "Akuma Homura", "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert dummyDict["Akuma Homura"].echoDict["type"] == "devil", "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert not dummyDict["Akuma Homura"].echoDict["purity"], "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        print("LoadJSONIntoDictOfObjects test passes")

    def TestWeightedRandom(self):
        inDict = {"homu": 2, "mado": 2, "saya": 1, "koko": 1}
        try:  # Test maximal integer limit
            ArenaUtils.weightedDictRandom(inDict, 5)
            raise AssertionError(
                "weightedDictRandom did not properly raise IndexError when given too large an integer!")
        except IndexError:
            pass
        for x in range(0, 5):
            if x == 1:
                continue
            assert(len(ArenaUtils.weightedDictRandom(inDict, x)) == x)
        test4 = ArenaUtils.weightedDictRandom(inDict, 4)
        for x in inDict:
            assert x in test4
        resultDict = {"homu": [0, 0, 0], "mado": [
            0, 0, 0], "saya": [0, 0, 0], "koko": [0, 0, 0]}
        for x in range(400):
            for y in range(3):
                for result in ArenaUtils.weightedDictRandom(inDict, y + 1):
                    resultDict[result][y] += 1
        # Not an exact test for all possible errors, but if these probabilities land perfectly despite something being wrong, then it's a huge fluke...
        assert abs(resultDict["homu"][0] / 400 - 1 /
                   3) < 0.075  # ~99% confidence here
        assert abs(resultDict["mado"][0] / 400 - 1 / 3) < 0.075
        assert abs(resultDict["saya"][0] / 400 - 1 / 6) < 0.075
        assert abs(resultDict["koko"][0] / 400 - 1 / 6) < 0.075
        assert abs(resultDict["homu"][1] / 400 - 19 / 30) < 0.075
        assert abs(resultDict["mado"][1] / 400 - 19 / 30) < 0.075
        assert abs(resultDict["saya"][1] / 400 - 11 / 30) < 0.075
        assert abs(resultDict["koko"][1] / 400 - 11 / 30) < 0.075
        assert abs(resultDict["homu"][2] / 400 - 52 / 60) < 0.075
        assert abs(resultDict["mado"][2] / 400 - 52 / 60) < 0.075
        assert abs(resultDict["saya"][2] / 400 - 38 / 60) < 0.075
        assert abs(resultDict["koko"][2] / 400 - 38 / 60) < 0.075
        print("WeightedDictRandom test passes")

    # TODO: Callback testss


if __name__ == "__main__":
    # execute only if run as a script
    thisTest = ArenaUtilsTest()
    thisTest.TestLoadJSONIntoDictOfObjects()
    thisTest.TestWeightedRandom()
