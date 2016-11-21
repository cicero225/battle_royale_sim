# Unit-testing for the Util functions in ArenaUtils.
import ArenaUtils # This must be run from the parent directory

class Dummy: # This might have to be more elaborate for some of the other tests
    def __init__(self, inDict, settings):
        self.echoDict = inDict

class ArenaUtilsTest:
    
    settings = {}; # This might have to be more elaborate for some of the other tests
    
    def __init__(self):
        pass    

    def LoadJSONIntoDictOfObjectsTest(self):
        path = "DummyJSON.json"
        dummyDict = ArenaUtils.LoadJSONIntoDictOfObjects(path, self.settings, Dummy)
        assert "Ultimate Madoka" in dummyDict, "LoadJSONIntoDictOfObjectsTest failed, top-level key missing"
        assert "Akuma Homura" in dummyDict, "LoadJSONIntoDictOfObjectsTest failed, top-level key missing"
        assert dummyDict["Ultimate Madoka"].echoDict["type"] == "divine", "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert dummyDict["Ultimate Madoka"].echoDict["purity"], "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert dummyDict["Akuma Homura"].echoDict["type"] == "devil", "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert not dummyDict["Akuma Homura"].echoDict["purity"], "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        print("LoadJSONIntoDictOfObjectsTest passes")
        
        
if __name__ == "__main__":
    # execute only if run as a script
    thisTest = ArenaUtilsTest()
    thisTest.LoadJSONIntoDictOfObjectsTest()