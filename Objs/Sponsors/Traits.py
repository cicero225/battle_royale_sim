# A holder object for arbitrary Traits and associated operations

class Traits(object):
    
    def __init__(self):
        self.starting_effects = {
            "Likes Weak": self.LikesWeak,
            "Likes Strong": self.LikesStrong,
            "Biased Male": self.BiasedMale,
            "Biased Female": self.BiasedFemale
        }
    
    @staticmethod
    def LikesWeak(sponsor, state):
        relationships = state["allRelationships"]
        for contestant in state["contestants"].values():
            if contestant.stats["combat ability"] <= 3:
                relationships.IncreaseFriendLevel(sponsor, contestant, 4, False)
                
    @staticmethod
    def LikesStrong(sponsor, state):
        relationships = state["allRelationships"]
        for contestant in state["contestants"].values():
            if contestant.stats["combat ability"] >= 7:
                relationships.IncreaseFriendLevel(sponsor, contestant, 4, False)
                
    @staticmethod
    def BiasedMale(sponsor, state):
        relationships = state["allRelationships"]
        for contestant in state["contestants"].values():
            if contestant.gender=='M':
                relationships.IncreaseFriendLevel(sponsor, contestant, 4, False)
            elif contestant.gender=='F':
                relationships.IncreaseFriendLevel(sponsor, contestant, -4, False)
                
    @staticmethod
    def BiasedFemale(sponsor, state):
        relationships = state["allRelationships"]
        for contestant in state["contestants"].values():
            if contestant.gender=='F':
                relationships.IncreaseFriendLevel(sponsor, contestant, 4, False)
            elif contestant.gender=='G':
                relationships.IncreaseFriendLevel(sponsor, contestant, -4, False)