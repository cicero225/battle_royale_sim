'''Writer which does not output anything.'''

class NullWriter(object):
    def __init__(self, statuses):
        pass
    def reset(self):
        pass
    def addTitle(self, title):
        pass
    def addEvent(self, desc, descContestants, state=None, preEventInjuries=None):
        pass
    def finalWrite(self, filepath, state):
        pass
    def addBigLine(self, line):
        pass
