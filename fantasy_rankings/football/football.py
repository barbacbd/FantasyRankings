from enum import Enum


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
    
    def __init__(self, htmlStr):
        self.rank: int = -1
        self.position: str = None
        self.name: str = None
        self.teamCode: str = None

        self.parse(htmlStr)
        
    def parse(self, htmlStr):
        '''Parse the data from the original HTML stream 
        obtained from the pulled source. For more information about
        the source see `webpage` below.
        '''
        splitHTML = [x for x in htmlStr.split(" ") if x]
        self.rank = int(float(splitHTML[0]))
        self.name = " ".join(splitHTML[1:len(splitHTML)-1])

        splitTeamAndPos = splitHTML[len(splitHTML)-1].split("-")
        self.position = splitTeamAndPos[0]
        if len(splitTeamAndPos) > 1:
            self.teamCode = splitTeamAndPos[1]

    def to_json(self):
        return {"Overall Rank": self.rank, "Player": self.name, "Position": self.position, "Team": self.teamCode}
            
    def __str__(self):
        '''String representation of the instance'''
        return f"{self.rank}. {self.name} {self.position}-{self.teamCode}"


class FFRankings:
    '''Base class for Fantasy Football Rankings'''

    def __init__(self, outputFile):
        self.rankedPlayers = []
        
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
        jsonData = []
        for playerData in playerDataList:
            jsonData.append(playerData.to_json())

        df = pd.DataFrame(jsonData)
        sheetName = "FantasyRankings"

        writer = pd.ExcelWriter(self.xlsxFilename, engine='xlsxwriter')
        df.to_excel(writer, sheet_name=sheetName, index=False)

	workbook  = writer.book
        worksheet = writer.sheets[sheetName]

        (max_row, max_col) = df.shape
        worksheet.set_column(0,  max_col - 1, 12)
        worksheet.autofilter(0, 0, max_row, max_col - 1)

        writer.save()

    def saveAsMarkdown(self):
        '''Save the current data to a markdown file'''
