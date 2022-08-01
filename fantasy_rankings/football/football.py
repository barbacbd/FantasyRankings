from enum import Enum
from datetime import datetime
import pandas as pd
from os.path import abspath, dirname, join
from jinja2 import Template, Environment
from ..templates.markdown import hyperlink
from collections import defaultdict


class Division(Enum):
    '''Class that contains all possibilities for NFL Divisions'''
    AFC_East  = 1
    AFC_North = 2
    AFC_South = 3
    AFC_West  = 4
    NFC_East  = 5
    NFC_North = 6
    NFC_South = 7
    NFC_West  = 8

    '''String name for the division'''
    __str__ = lambda x: " ".join(x.name.split("_"))


class FantasyLeagueScoring(Enum):
    '''Type of scoring used for Fantasy Football League
    
    Custom scoring types are unsupported
    '''
    STD = 1
    HALF_PPR = 2
    PPR = 3


class NFLTeam:
    '''Simple Class to hold information about a team
    '''

    def __init__(self, teamID, teamCode, mascot, division):
        self.teamID = teamID
        self.teamCode = teamCode
        self.teamName = mascot
        self.division = division

    def __str__(self):
        return f"{self.teamID} {self.teamName}"


'''Current Tuple containing all NFL Team information'''
Teams = (
    NFLTeam("New England",   "NE",  "Patriots",   Division.AFC_East),
    NFLTeam("Miami",         "MIA", "Dolphins",   Division.AFC_East),
    NFLTeam("New York",      "NYJ", "Jets",       Division.AFC_East),
    NFLTeam("Buffalo",       "BUF", "Bills",      Division.AFC_East),
    NFLTeam("Cincinnati",    "CIN", "bengals",    Division.AFC_North),
    NFLTeam("Pittsburgh",    "PIT", "Steelers",   Division.AFC_North),
    NFLTeam("Baltimore",     "BAL", "Ravens",     Division.AFC_North),
    NFLTeam("Cleveland",     "CLE", "Browns",     Division.AFC_North),
    NFLTeam("Houston",       "HOU", "Texans",     Division.AFC_South),
    NFLTeam("Indianapolis",  "IND", "Colts",      Division.AFC_South),
    NFLTeam("Tennessee",     "TEN", "Titans",     Division.AFC_South),
    NFLTeam("Jacksonville",  "JAC", "Jaguars",    Division.AFC_South),
    NFLTeam("Las Vegas",     "LV",  "Raiders",    Division.AFC_West),
    NFLTeam("Denver",        "DEN", "Broncos",    Division.AFC_West),
    NFLTeam("Los Angeles",   "LAC", "Chargers",   Division.AFC_West),
    NFLTeam("Kansas City",   "KC",  "Chiefs",     Division.AFC_West),
    NFLTeam("Dallas",        "DAL", "Cowboys",    Division.NFC_East),
    NFLTeam("Philidelphia",  "PHI", "Eagles",     Division.NFC_East),
    NFLTeam("Washington",    "WAS", "Commanders", Division.NFC_East),
    NFLTeam("New York",      "NYG", "Giants",     Division.NFC_East),
    NFLTeam("Detroit",       "DET", "Lions",      Division.NFC_North),
    NFLTeam("Minnesota",     "MIN", "Vikings",    Division.NFC_North),
    NFLTeam("Green Bay",     "GB",  "Packers",    Division.NFC_North),
    NFLTeam("Chicago",       "CHI", "Bears",      Division.NFC_North),
    NFLTeam("New Orleans",   "NO",  "Saints",     Division.NFC_South),
    NFLTeam("Tampa Bay",     "TB",  "Buccaneers", Division.NFC_South),
    NFLTeam("Atlanta",       "ATL", "Falcons",    Division.NFC_South),
    NFLTeam("Carolina",      "CAR", "Panthers",   Division.NFC_South),
    NFLTeam("Seattle",       "SEA", "Seahawks",   Division.NFC_West),
    NFLTeam("Arizona",       "ARI", "Cardinals",  Division.NFC_West),
    NFLTeam("San Francisco", "SF",  "49ers",      Division.NFC_West),
    NFLTeam("Los Angeles",   "LAR", "Rams",       Division.NFC_West),
)

FREE_AGENT_CODE = "FA"


class FFPlayer:
    '''FantasyFootball Player. This is a player information
    class that will contain the basics such as team, rank,
    and position. 
    '''
    def __init__(self, name, rank, position, teamCode=None):
        self.rank: int = rank
        self.position: str = position
        self.name: str = name
        self.teamCode: str = teamCode
        self.link: str = None
        self.positionRank: int = None

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


def FFPlayerAsMarkdown(player):
    '''Convert player information to Markdown text
    '''
    if player.link is not None:
        if player.teamCode:
            return f"{player.rank}. {hyperlink(player.name, player.link)} {player.position}-{player.teamCode}"
        return f"{player.rank}. {hyperlink(player.name, player.link)} {player.position}"
    return str(player)


def FFPlayerAsMarkdownTable(player):
    '''Conver player information into a table entry'''
    
    


class FFRankings:
    '''Base class for Fantasy Football Rankings'''

    def __init__(self, source, outputFile):
        self.title = f"## {source} Fantasy Football Draft Rankings"
        self.description = f'''
The data contained in this file is the result of scraping fantasy football draft ranking information
from {source} on {datetime.now().month}/{datetime.now().day}/{datetime.now().year}. 
        
All information contained in this file should be utilized with caution as the rankings may change
at the discretion of Fantasy Pros. Information is only considered valid at the time that the 
information is scraped. 
        '''
        self.rankedPlayers = defaultdict(list)
        self._outputFilePrefix = outputFile
        
        self.rankingEndpoints = {
            FantasyLeagueScoring.STD: None,
            FantasyLeagueScoring.HALF_PPR: None,
            FantasyLeagueScoring.PPR: None
        }
        
        self.xlsxFilename = f"{outputFile}.xlsx"
        self.mdFilename   = f"{outputFile}.md"

    def run(self):
        if self.scrape():
            self.saveAsXlsx()
            self.saveAsMarkdown()
        
    def scrape(self):
        ''' Base class does not implement this function, child Must'''
        raise NotImplementedError(f"FFRankings does not implement scrape")
        
    def saveAsXlsx(self):
        '''Save the curent data to an xlsx file'''
        
        for scoringType, players in self.rankedPlayers.items():
            
            filename = self._outputFilePrefix + "_" + scoringType.name + ".xlsx"
                    
            jsonData = []
            for playerData in players:
                jsonData.append(playerData.to_json())

            df = pd.DataFrame(jsonData)
            sheetName = "FantasyRankings"

            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            df.to_excel(writer, sheet_name=sheetName, index=False)
            
            workbook  = writer.book
            worksheet = writer.sheets[sheetName]

            (max_row, max_col) = df.shape
            worksheet.set_column(0,  max_col - 1, 12)
            worksheet.autofilter(0, 0, max_row, max_col - 1)

            writer.save()

    def mdBody(self):
        raise NotImplementedError("FFRankings does not implement mdBody")

    def saveAsMarkdown(self):
        '''Save the current data to a markdown file'''
        output = self.title + "\n\n" + self.description + "\n\n" + self.mdBody()
        
        with open(self.mdFilename, "w") as mdFile:
            mdFile.write(output)
