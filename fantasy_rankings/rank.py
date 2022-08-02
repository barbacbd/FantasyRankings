from collections import defaultdict


class BaseRankings:
    
    def __init__(self, title, description):
        self.title = title
        self.description = description
        
        self.rankedPlayers = defaultdict(list)