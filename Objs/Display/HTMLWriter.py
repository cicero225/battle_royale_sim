"""A dumb very specific html writer, because I don't want to figure out the various library options."""

import re

class HTMLWriter(object):

    header = """<!DOCTYPE html>
<html>
<head>
<style>
eventnormal {
    color: black;
}
p {
    text-align: center;
}
character {
    color: orange;
}
banner {
    text-align: center;
    font-size: 200%;
}
img {
    width: 128px
}
</style>
</head>
<body>"""

    footer = """</body>
</html>"""

    def __init__(self):
        self.bodylist = [self.header]
    
    def reset(self):
        self.bodylist = [self.header]
    
    def wrap(self, text, wrapname):
        return "<"+wrapname+">\n"+text+"\n</"+wrapname+">\n"
    
    def addTitle(self, title):
        self.bodylist.insert(1,self.wrap(self.wrap(title, "banner"),"p"))
        
    def addDay(self, day):
        self.addTitle("Day "+str(day))
        
    def addEvent(self, desc, descContestants):
        tempStringList = []
        for contestant in descContestants:
            tempStringList.append("<img src='"+contestant.imageFile+"'>")
        tempStringList.append("<br>")
        tempStringList.append(self.wrap(desc, "eventnormal"))
        self.bodylist.append(self.wrap('\n'.join(tempStringList),"p"))
        
    def finalWrite(self, filepath):
        self.bodylist.append(self.footer)
        with open(filepath, 'w') as target:
            for line in self.bodylist:
                target.write(line)
                
    def addBigLine(self, line):
        self.bodylist.append(self.wrap(line, "p"))