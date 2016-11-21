import json


def LoadJSONIntoDictOfObjects(path,settings,objectType):
#####
# Args: path is the path to the json.
#       settings is the settings dict, itself loaded from JSON (but not by this)
#       objectType is the class of the object (can be passed in Python)
#
# Returns: dict with keys corresponding to object names and values corresponding to the objects formed. This is effectively
# a table of these objects. (A table of contestants, sponsors, etc.)
#
# Notes: Path is typically something like os.path.join('Contestants', 'Constestant.json') but let's not assume that.
#
#####
    with open(path) as file:
        fromFile = json.load(file)

    objectDict = {}
    for name in fromFile:
        objectDict[name] = objectType(fromFile[name], settings) # Constructor should \
                                                                  # take in dict and settings (also a dict)
    return objectDict                                                              