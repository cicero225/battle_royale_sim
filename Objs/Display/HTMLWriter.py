"""A dumb very specific html writer, because I don't want to figure out the various library options."""

import html
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
contestant {
    color: DarkBlue;
}
item {
    color: Red;
}
negative {
    color: Red;
}
positive {
    color: Green;
}
status {
    color: Brown;
}
sponsor {
    color: DarkGoldenRod;
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

    def __init__(self, statuses):
        self.bodylist = []
        self.statuses = statuses
        self.contestant_regexes = {}

    def reset(self):
        self.bodylist = []

    @staticmethod
    def wrap(text, wrapname, escape=False):
        if escape:
            text = html.escape(text)
            wrapname = html.escape(wrapname)
        return "<" + wrapname + ">\n" + text + "\n</" + wrapname + ">\n"

    def addTitle(self, title, escape=True):
        if escape:
            title = html.escape(title)
        self.bodylist.insert(1, HTMLWriter.wrap(HTMLWriter.wrap(title, "banner"), "p"))

    @staticmethod
    def massInsertTag(desc, findString, insertString):
        findString = html.escape(findString)
        insertString = html.escape(insertString)
        stringList = desc.split(findString)        
        if len(stringList) == 1:
            return desc
        for i, entry in enumerate(stringList):
            # Massive kludge. I didn't realize this would be a problem, so a lot of the images are named the same as the characters. Then again, this whole object is a kludge :p.
            last_entry = stringList[i - 1] if i > 0 else " "
            next_entry = stringList[i + 1] if i < len(stringList) - 1 else " "
            if last_entry and not last_entry[-1].isalnum() and last_entry[-1] not in ["/", "<"] and entry and not entry[0].isalnum() and entry[0] != ">" and not entry.lower().startswith('.jpg') and not entry.lower().startswith('.png') and not entry.lower().startswith('.gif'):
                stringList[i] = "</" + insertString + ">" + stringList[i]
            if i < len(stringList) - 1:                
                if entry and not entry[-1].isalnum() and entry[-1] not in ["/", "<"] and next_entry and not next_entry[0].isalnum() and next_entry[0] != ">" and not next_entry.lower().startswith('.jpg') and not next_entry.lower().startswith('.png') and not next_entry.lower().startswith('.gif'):
                    stringList[i] = stringList[i] + "<" + insertString + ">"
        return findString.join(stringList)

    def colorize(self, desc, state):
        # This would be more efficient if handled at the event level, but then it'd have to be worried about, etc. and require rewriting. Better to just waste a little computation dealing with it here.
        for x in state["contestants"]:
            desc = self.massInsertTag(desc, x, "contestant")
        for x in state["sponsors"]:
            desc = self.massInsertTag(desc, x, "sponsor")
        for x in state["items"].values():
            desc = self.massInsertTag(desc, x.friendly, "item")
        for x in state["statuses"].values():
            desc = self.massInsertTag(desc, x.friendly, "status")
        return desc

    def addEvent(self, desc, descContestants, state=None, preEventInjuries=None, escape=True):
        if escape:
            desc = html.escape(desc)
            # Convert \n to <br/>
            desc = desc.replace("\n", "<br/>")
        tempStringList = []
        for contestant in descContestants:
            if state is not None:
                extensionString = ""
                if hasattr(contestant, "statuses") and preEventInjuries.get(str(contestant), False) and contestant.hasThing("Injury"):
                    extensionString += ' (Injured)'
                if hasattr(contestant, "statuses") and contestant.hasThing("Hypothermia"):
                    extensionString += ' (Hypothermic)'
                if extensionString:
                    # We could use setdefault but that would defeat the purpose of not compiling the regex.
                    potentialRegex = self.contestant_regexes.get(str(contestant))
                    if potentialRegex is None:
                        potentialRegex = re.compile(r"(?<![\w\<])(" + re.escape(html.escape(str(contestant))) + r")(?![\w\>])")
                        self.contestant_regexes[str(contestant)] = potentialRegex
                    desc = potentialRegex.sub(html.escape(str(contestant)) + extensionString, desc)
            tempStringList.append("<img src='" + html.escape(contestant.imageFile) + "'>")
        tempStringList.append("<br>")
        tempStringList.append(HTMLWriter.wrap(desc, "eventnormal"))
        self.bodylist.append(HTMLWriter.wrap('\n'.join(tempStringList), "p"))

    def finalWrite(self, filepath, state):
        with open(filepath, 'w') as target:
            target.write(self.header)
            for line in self.bodylist:
                target.write(self.colorize(line, state))
            target.write(self.footer)

    def addBigLine(self, line, escape=True):
        if escape:
            line = html.escape(line)
        self.bodylist.append(HTMLWriter.wrap(line, "p"))
