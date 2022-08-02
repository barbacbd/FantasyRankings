import requests
from bs4 import BeautifulSoup
from .football import FFRankings, FantasyLeagueScoring
from ..player import Player, SetPositionRanks, CreatePositionTable, AdjustTableToMarkdown
from collections import defaultdict
from json import dump, load
from os.path import exists


class FantasyProsFootball(FFRankings):

    '''Class to scrape all fantasy football draft information from Fantasy Pros'''
    
    def __init__(self):
        super(FantasyProsFootball, self).__init__("Fantasy Pros", "FantasyProsFootballDraft")
        self.outputFile = "FantasyProsFootballDraft"
        self.baseWebpage = "https://www.fantasypros.com"
        
        self.rankingEndpoints[FantasyLeagueScoring.STD] = "/nfl/cheatsheets/top-players.php"
        self.rankingEndpoints[FantasyLeagueScoring.HALF_PPR] = "/nfl/cheatsheets/top-half-ppr-players.php"
        self.rankingEndpoints[FantasyLeagueScoring.PPR] = "/nfl/cheatsheets/top-ppr-players.php"
        
        self.playerEndpoints = defaultdict(list)

    def scrape(self) -> bool:
        '''Scrape the data from the draft rankings endpoint.
        Set the Draft ranking information to this instance.
        
        :return: True on success
        '''
        for scoringType, endpoint in self.rankingEndpoints.items():
            
            if endpoint is None:
                continue
                        
            site = self.baseWebpage + endpoint
            webpage = requests.get(site)
            page_html = BeautifulSoup(webpage.text, 'html.parser')

            playerListDivs = page_html.find_all("div", {"class": "player-list"})
            if 0 > len(playerListDivs) > 1:
                return False

            playerListDiv = playerListDivs[0]

            # clear/reset the player information
            self.rankedPlayers[scoringType].clear()
            
            for ul in playerListDiv.find_all('ul'):
                liDataAsPlayers = []
                for li in ul.find_all('li'):
                    player = self._parsePlayerHtmlStr(li.text.replace(u'\xa0', u' '))

                    href = li.find("a").get("href")
                    self.playerEndpoints[player.name] = self.baseWebpage+href
                    player.link = self.playerEndpoints[player.name]
                    
                    liDataAsPlayers.append(player)

                self.rankedPlayers[scoringType].extend(liDataAsPlayers)

        return True
        
    def _setPositionRanks(self):
        for _, players in self.rankedPlayers.items():
            SetPositionRanks(players)

    def _parsePlayerHtmlStr(self, htmlStr):
        '''Parse the data from the original HTML stream 
        obtained from the pulled source. For more information about
        the source see `webpage` below.
        '''
        splitHTML = [x for x in htmlStr.split(" ") if x]
        rank = int(float(splitHTML[0]))
        name = " ".join(splitHTML[1:len(splitHTML)-1])

        splitTeamAndPos = splitHTML[len(splitHTML)-1].split("-")
        position = splitTeamAndPos[0]
        teamCode = None
        if len(splitTeamAndPos) > 1:
            teamCode = splitTeamAndPos[1]
        
        return Player(name, rank, position, teamCode)
    
    def saveAsMarkdown(self):
        '''
        Page 1 = Base page with information and links to other pages
        Page 2 = PPR Rankings 
            - Table of position ranks
            - All Rankings 
        Page 3 = STD Rankings 
            - Table of position ranks
            - All Rankings 
        Page 4 = HALF Rankings 
            - Table of position ranks
            - All Rankings 
        '''

        self._setPositionRanks()
                
        mdFileLinks = []
        childFiles = []
        
        for key, players in self.rankedPlayers.items():
            # Create the specific files
            filename = self.outputFilePrefix + key.name + ".md"
            childFiles.append(filename)
            mdFileLinks.append(f"- [{key.name}]({filename})")
            
            # Create the positional ranking table
            table = CreatePositionTable(players)
            table = AdjustTableToMarkdown(table)
            
            tableHeader = "| " + " | ".join(list(table.keys()))
            tableFormat = ["| :--- "] * len(list(table.keys()))
            tableFormat = "".join(tableFormat) + "|"
            
            mdTable = f"{tableHeader}\n{tableFormat}\n"
            tableLen = len(table[list(table.keys())[0]])

            for i in range(tableLen):
                lineData = []
                for key in table.keys():
                    lineData.append(table[key][i])
                
                line = " | " + " | ".join(lineData)
                mdTable += f"{line}\n"
                
            
            with open(filename, "w+") as _file:
                _file.write(
                    f"{self.title} - {key}\n\n"
                )
                
                _file.write(
                    f"The file contains the {key} rankings. This includes the"
                    "overall rankings as well as the positional rankings."
                )
                
                _file.write("## Overall Rankings\n\n")
                for player in players:
                    _file.write(f"{player.markdown}\n")
                
                _file.write("\n\n")
                
                _file.write("## Position Ranks\n\n")
                _file.write(mdTable)
                
                _file.write
        
        # write the base markdown file.
        with open(self.outputFilePrefix+ ".md", "w+") as _file:
            _file.write(f"{self.title}\n\n{self.description}\n\n")
            _file.write("## League Type Rankings\n\n")
            for link in mdFileLinks:
                _file.write(f"{link}\n")
        
        return {
            "base": self.outputFilePrefix+ ".md",
            "children": childFiles
        }


def run():
    ''' Run the web scraping for fantasy pros.
    '''
    fpf = FantasyProsFootball()
    outputData = fpf.run()
    
    jsonData = {}
    
    if exists("readme.json"):
        with open("readme.json", "rb") as jsonFile:
            jsonData = load(jsonFile)

    if "football" not in jsonData:
        jsonData["football"] = {}
        
        if fpf.title not in jsonData["football"]:
            jsonData["football"][fpf.source] = {}
            
    jsonData["football"][fpf.source] = outputData
    
    with open("readme.json", "w") as jsonFile:
        dump(jsonData, jsonFile, indent=4)