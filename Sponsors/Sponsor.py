# It abruptly occurs to me that events with sponsors are going to need their own special handling to properly reflect the effect of sponsor relationships
# on contestants. Sponsors should also "like" contestants who do certain events. I'm too beat to deal with that right now. (gifts should probably make contestants like specific sponsors more, for whatever that's worth)

from __future__ import division # In case of Python 2+. The Python 3 implementation is way less dumb.

class Sponsor(object):

    def __init__(self, name, inDict, settings):  
        self.name = name
        self.setting = settings
        self.imageFile = inDict['imageFile']
        self.stats = inDict['stats']

