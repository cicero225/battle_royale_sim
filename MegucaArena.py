import json
import os
import random #A not very good random library, but probably fine for our purposes

from Contestants.Contestant import Contestant
from Events.Event import Event
from Items.Item import Item
from Sponsors.Sponsor import Sponsor
from World.World import World

# Initial Setup

# Import Settings from JSON -> going to make it a dictionary
with open('Settings.json') as settings_file:
    settings = json.load(settings_file)

# List of settings as I come up with them. It can stay as a dict.
# traitRandomness = 3
# numContestants = 24 # Program should pad or randomly remove contestants as necessary


# Import and initialize contestants -> going to make it dictionary name : (imageName,baseStats)
with open(os.path.join('Contestants', 'Constestant.json')) as constestants_file:
    constestantsFromFile = json.load(constestants_file)

contestantNames = constestantsFromFile.keys()

# If number of contestants in settings less than those found in the json, randomly remove some
if settings['numContestants'] < len(contestantNames):
    contestantNames = random.sample(contestantNames, settings['numContestants'])
    
# Make dictionary of contestants    
for contestantName in contestantNames:
    constestants[contestantName] = Constestant(constestantsFromFile[contestantName], settings) # Constructor should \
     # take in dict and settings (also a dict)
     
# If number of contestants in settings more than those found in the json, add Rando Calrissians
for i in range(len(contestantNames),settings['numContestants']):
    constestants['Rando Calrissian ' + i] =  Constestant('Rando Calrissian ' + i, pass, settings) # Constructor should \
     # also take in string, image, settings and make full random stats (need Rando image to put here)
     
