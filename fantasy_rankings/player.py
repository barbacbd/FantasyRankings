from collections import defaultdict
from .util import hyperlink



class Player:
    '''Basic player information class that will contain data 
    such as team, rank, and position. 
    '''
    def __init__(self, name, rank, position, teamCode=None):
        self.rank: int = rank
        self.position: str = position
        self.name: str = name
        self.teamCode: str = teamCode
        self.link: str = None
        self.positionRank: int = None

    @property
    def anchor(self):
        '''Deterministic value for a player to be linked using markdown
        anchors.
        '''
        anchorData = [x.lower() for x in self.name.split()] + [str(self.rank)]
        return "-".join(anchorData)

    def to_json(self):
        data = {"Overall Rank": self.rank, "Player": self.name, "Position": self.position}
        if self.teamCode:
            data["Team"] = self.teamCode 
            
        return data
    
    def __str__(self):
        '''String representation of the instance'''
        if self.teamCode:
            return f"{self.rank}. {self.name} {self.position}-{self.teamCode}"
        return f"{self.rank}. {self.name} {self.position}"

    @property
    def markdown(self):
        if self.link is not None:
            if self.teamCode:
                return f"{self.rank}. {hyperlink(self.name, self.link)} {self.position}-{self.teamCode}"
            return f"{self.rank}. {hyperlink(self.name, self.link)} {self.position}"
        return str(self)



def CreatePositionTable(players):
    '''Create the markdown for each player and add that information 
    to the final datatype, so that there is a link '''
    positionTable = defaultdict(list)
    
    for player in players:
        positionTable[player.position.upper()].append(hyperlink(player.name, player.link))
    
    return positionTable


def AdjustTableToMarkdown(table):
    ''' Create a table or 2D array that contains blank spaces "-" where 
    a player did not exist. For instance there are 20 players of one type
    and 10 of another, there will be 10 blank spaces.
    '''
    maxLen = max([len(x) for _, x in table.items()])
    
    for key, playerList in table.items():
        addons = ["-"] * (maxLen - len(playerList))
        
        playerList.extend(addons)

    return table


def SetPositionRanks(players):
    '''Given the list of players, set the positional rank for that player'''
    ranks_by_position = {}
    
    for player in players:
        position = player.position.upper()
        
        if position not in ranks_by_position:
            ranks_by_position[position] = 0

        ranks_by_position[position] += 1
        player.positionRank = ranks_by_position[position]