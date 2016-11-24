# Unit-testing for the Util functions in ArenaUtils.
import ArenaUtils
import io

class Dummy: # This might have to be more elaborate for some of the other tests
    def __init__(self, name, inDict, settings):
        self.echoDict = inDict
        self.name = name

class ArenaUtilsTest:
    
    settings = {}; # This might have to be more elaborate for some of the other tests
    
    def __init__(self):
        pass    

    def TestLoadJSONIntoDictOfObjects(self):
        this_file = io.StringIO('''{"Ultimate Madoka": {"type": "divine","purity": true},
        "Akuma Homura": {"type": "devil","purity": false}}''') # simulated file, keeping it enclosed in this method
        dummyDict = ArenaUtils.LoadJSONIntoDictOfObjects(this_file, self.settings, Dummy)
        assert "Ultimate Madoka" in dummyDict, "LoadJSONIntoDictOfObjectsTest failed, top-level key missing"
        assert "Akuma Homura" in dummyDict, "LoadJSONIntoDictOfObjectsTest failed, top-level key missing"
        assert dummyDict["Ultimate Madoka"].name == "Ultimate Madoka", "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert dummyDict["Ultimate Madoka"].echoDict["type"] == "divine", "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert dummyDict["Ultimate Madoka"].echoDict["purity"], "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert dummyDict["Akuma Homura"].name == "Akuma Homura", "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert dummyDict["Akuma Homura"].echoDict["type"] == "devil", "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        assert not dummyDict["Akuma Homura"].echoDict["purity"], "LoadJSONIntoDictOfObjectsTest failed, object data incorrect"
        print("LoadJSONIntoDictOfObjectsTest passes")
        
    
        
        
if __name__ == "__main__":
    # execute only if run as a script
    thisTest = ArenaUtilsTest()
    thisTest.TestLoadJSONIntoDictOfObjects()