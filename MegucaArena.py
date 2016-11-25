import json
import os
import random #A not very good random library, but probably fine for our purposes

from Contestants.Contestant import Contestant
from Items.Item import Item
from Sponsors.Sponsor import Sponsor
from World.World import World
import ArenaUtils
import Events


# Initial Setup:

# Import Settings from JSON -> going to make it a dictionary
with open('Settings.json') as settings_file:
    settings = json.load(settings_file)

# List of settings as I come up with them. It can stay as a dict.
# traitRandomness = 3
# numContestants = 24 # Program should pad or randomly remove contestants as necessary
# eventRandomness = 0.5 # Percent range over which the base weights of events varies from json settings
# statInfluence = 0.3 # How much stats influence event weightings, calculated as (1+influence)^(stat-5)
# objectInfluence = 1 # How much objects in inventory affect events. The default 1 uses the base stats.
# Note that objects that fully disable a event should still do so!


# Initialize Arena State

# Initialize Events
events = ArenaUtils.LoadJSONIntoDictOfEventObjects(os.path.join('Contestants', 'Contestant.json'),settings)

# Import and initialize contestants -> going to make it dictionary name : (imageName, baseStats...)
contestants = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Contestants', 'Contestant.json'),settings,Contestant)
# If number of contestants in settings less than those found in the json, randomly remove some
contestantNames = constestantsFromFile.keys()
if settings['numContestants'] < len(contestantNames):
    contestantNames = random.sample(contestantNames, len(contestantNames)-settings['numContestants'])
    for remove in contestantNames:
        del contestants[remove]
# If number of contestants in settings more than those found in the json, add Rando Calrissians
for i in range(len(contestantNames),settings['numContestants']):
    contestants['Rando Calrissian ' + i] =  Contestant('Rando Calrissian ' + i, pass, settings) # Constructor should \
     # also take in string, image, settings and make full random stats (need Rando image to put here)

# Import and initialize sponsors -> going to make it dictionary name : (imageName,baseStats...)
# baseStats =  weight (probability relative to other sponsors, default 1), objectPrefs (any biases towards or away any \
# from any type of object gift, otherwise 1, Anything else we think of)
# No placeholder sponsors because of the way it is handled.
sponsors = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Sponsors', 'Sponsor.json'),settings,Sponsor)

# Import and initialize Items -> going to make it dictionary name : (imageName,baseStats...)
items = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Items', 'Item.json'),settings,Item)

#Initialize World - Maybe it should have its own settings?
arena = World(settings) #Maybe other arguments in future, i.e. maybe in an extended world items can be found on the ground, but leaving this as-is for now.

# Run simulation
# If we're going to have a cornucopia, we should remember to set up some way to have a special turn: maybe as a separate object?
# In any case a special turn would have unique base event weights.

# General pseudocode idea
# Sample contestants randomly
# Go through contestants
# For each contestant, go through event list and poll their weights + contestant weight modifiers (base weights + object and relationship modifiers)
# (Remember that base event weights may change based on turn)
# (For multi-contestant events, there should also be a weight stored for a) being a "participant" on the side of whoever started the event and b) being a "victim"
# These should affect the final weight used (I should figure out a formula for this) and also be used to pick secondary participants/victims.
# Using these weights, pick an event and call its method. If multi-contestant, also make sure not to let them roll another event.
# Check that this turn has not killed everyone. If it has, redo the _entire_ turn (it's the only fair way).
# Then print results into HTML (?) or whatever makes sense
# Repeat.
