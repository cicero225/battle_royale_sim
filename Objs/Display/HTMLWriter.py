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

    # Adds a basic event with some formatting. Use addStructuredEvent for canonical EventOutput outputs.
    def addEvent(self, desc, descContestants, state=None, preEventInjuries=None, escape=True, output_string=False):
        if escape:
            desc = html.escape(desc)
            # Convert \n to <br/>
            desc = desc.replace("\n", "<br/>")
        tempStringList = []
        if descContestants:
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
                if contestant.imageFile is not None:
                    tempStringList.append("<img src='" + html.escape(contestant.imageFile) + "'>")
            tempStringList.append("<br>")
        tempStringList.append(HTMLWriter.wrap(desc, "eventnormal"))
        outputString = '\n'.join(tempStringList)
        if output_string:
            return outputString
        self.bodylist.append(HTMLWriter.wrap(outputString, "p"))
    
    # If we were enforcing typing, event_output is Event.EventOutput
    # This is canoncical output for events.
    def addStructuredEvent(self, event_output, state, preEventInjuries):
        from ..Events.Event import Event  # This utility function should really be made more general...
        output_pieces = []
        desc = event_output.description
        if event_output.dead or event_output.injuries:
            desc += "\n"
        if event_output.dead:           
            if event_output.list_killers:
                # Unfortunately, this dict is the exact reverse of the order we want this.
                reverse_kill_dict = {}
                for killed, killer in event_output.killer_dict.items():
                    reverse_kill_dict.setdefault(killer, []).append(killed)
                for killer, killed in reverse_kill_dict.items():
                    is_str = isinstance(killed[0], str)
                    desc += '\n' + killer +  ' kills ' + Event.englishList(killed, not is_str)
            else:
                is_str = isinstance(event_output.dead[0], str)
                desc += '\nKilled: ' + Event.englishList(event_output.dead, not is_str)          
        if event_output.injuries:
            is_str = isinstance(event_output.injuries[0], str)
            desc += '\nInjured: ' + Event.englishList(event_output.injuries, not is_str)
        output_pieces.append(self.addEvent(desc, event_output.display_items, state, preEventInjuries, output_string=True))
        if event_output.loot_table:
            # This will likely need some work.
            lootedList = []
            desc = ""
            for name, items in event_output.loot_table.items():
                lootedList.extend(items)
                # Because some items may choose not to display (e.g. Dossiers for dead people), we need to check if the resulting string is even popualted.
                maybe_string = Event.englishList(items)
                if maybe_string:
                    desc += name + " looted " + maybe_string + "\n"
            output_pieces.append(self.addEvent(desc, lootedList, state, preEventInjuries, output_string=True))
        self.bodylist.append(HTMLWriter.wrap('<br/>'.join(output_pieces), "p"))
        
    def addEmptyLines(self, num_lines):
        self.bodylist.append(''.join('<br/'*num_lines))

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
