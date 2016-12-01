"""Utility functions for battle royale sim"""
import json
import sys

def StrToClass(string):
    return getattr(sys.modules[__name__], string)

def LoadJSONIntoDictOfEventObjects(path, settings): # This is unfortunately going to be pretty specific. It could be generalized
    # more, but that'd take more work
    try:
        with open(path) as file:
            fromFile = json.load(file)
    except TypeError:
        fromFile = json.load(path)
    
    objectDict = {}
    for name in fromFile:
        thisClass = StrToClass(name)
        objectDict[name] = thisClass(name, fromFile[name], settings) # Constructor should \
                                                                  # take in name, dict and settings (also a dict)
    return objectDict                                                              

def LoadJSONIntoDictOfObjects(path, settings, objectType):
    """
    # Args: path is the path or file handle to the json
    #       settings is the settings dict, itself loaded from JSON (but not by this)
    #       objectType is the class of the object (can be passed in Python)
    #
    # Returns: dict with keys corresponding to object names and values corresponding to the objects formed. This is effectively
    # a table of these objects. (A table of contestants, sponsors, etc.)
    #
    # Notes: Path is typically something like os.path.join('Contestants', 'Constestant.json') but let's not assume that.
    #
    """
    try:
        with open(path) as file:
            fromFile = json.load(file)
    except TypeError:
        fromFile = json.load(path)

    objectDict = {}
    for name in fromFile:
        objectDict[name] = objectType(name, fromFile[name], settings) # Constructor should \
                                                                  # take in dict and settings (also a dict)
    return objectDict 
    