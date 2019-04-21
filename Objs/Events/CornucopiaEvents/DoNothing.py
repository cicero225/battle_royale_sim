from Objs.Events.Event import Event

def cornucopiaEndPhaseCallback(thisPhase, PRINTHTML, state):
    if thisPhase == "Cornucopia":
        state["events"]["DoNothing"].eventStore.setdefault("CornucopiaDoNothing", [])
        skippers = state["events"]["DoNothing"].eventStore["CornucopiaDoNothing"]
        if skippers:
            thisWriter = state.get("thisWriter")
            if thisWriter is not None:
                state["thisWriter"].addEvent("The following contestants chose to skip the Cornucopia: " + Event.englishList(skippers), skippers)
            else:
                print("The following contestants chose to skip the Cornucopia: " + Event.englishList(skippers), skippers)
            skippers.clear()

Event.registerInsertedCallback(
    "postPhaseCallbacks", cornucopiaEndPhaseCallback)

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    # This is a dummy event, representing the character not participating. For display purposes, these are only displayed at the end of the turn.
    listNothing = self.eventStore.setdefault("CornucopiaDoNothing", [])
    listNothing.append(mainActor)
    return (None, [mainActor], [])

Event.registerEvent("DoNothing", func)