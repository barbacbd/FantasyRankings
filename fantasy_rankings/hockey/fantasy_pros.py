import requests
from bs4 import BeautifulSoup
from .hockey import FHRankings
from ..player import Player, SetPositionRanks, CreatePositionTable, AdjustTableToMarkdown
from collections import defaultdict
from json import dump, load
from os.path import exists
import re


class FantasyProsHockey(FHRankings):

    '''Class to scrape all fantasy hockey draft information from Fantasy Pros'''
    
    TableFields = [
        'Rank',
        'Player/Team',
        'PositionRank',
        'YahooRank',
        'ESPNRank',
        'CBSRank',
        'AverageRank'
    ]
    
    def __init__(self):
        super(FantasyProsHockey, self).__init__("Fantasy Pros", "FantasyProsHockeyDraft")
        self.outputFile = "FantasyProsHockeyDraft"
        self.baseWebpage = "https://www.fantasypros.com"
        
        self.rankingsPage = "/nhl/adp/overall.php"
        
        self.playerEndpoints = defaultdict(list)

    def scrape(self) -> bool:
        '''Scrape the data from the draft rankings endpoint.
        Set the Draft ranking information to this instance.
        
        :return: True on success
        '''
        page = self.baseWebpage + self.rankingsPage
        webpage = requests.get(page)
        page_html = BeautifulSoup(webpage.text, 'html.parser')

        playerData = page_html.find_all("div", {"class": "mobile-table"})
        
        if 0 > len(playerData) > 1:
                return False

        playerData = playerData[0]
        
        data = []
        links = []
        for tr in playerData.find_all("tr"):
            tds = tr.find_all('td')
            
            for td in tds:
                a = td.find('a')
                if a:
                    if a.get('href'):
                        links.append(a.get('href'))
            
            localData = [elem.text.strip() for elem in tds]
            data.extend(localData)
            if data:
                break
        
        if len(data) == 0:
            print("Found no data")
            return False
        
        if len(data) % len(FantasyProsHockey.TableFields) != 0:
            print(f"Data is not in increments of {len(FantasyProsHockey.TableFields)}")
            return False

        if len(links) != int(len(data) / len(FantasyProsHockey.TableFields)):
            print(f"Number of players does not match player links: {int(len(data) / len(FantasyProsHockey.TableFields))} != {len(links)}")
            return False
        
        self.rankedPlayers.clear()
        for i in range(0, len(data), len(FantasyProsHockey.TableFields)):
            p = self._createPlayer(data[i:i+len(FantasyProsHockey.TableFields)], None)
            link = links[int(p.rank)-1]
            p.link = self.baseWebpage + "".join(link.split())
            self.rankedPlayers[p.rank] = p

        return True
    
    def _createPlayer(self, playerData, link=None):
        rank = int(playerData[0])
        
        # regex string splitting for the position and rank
        match = re.match(r"([a-z]+)([0-9]+)", playerData[2], re.I)
        position = None
        positionRank = 0
        
        if match:
            items = match.groups()
            position = items[0]
            positionRank = items[1]
        
        nameAndTeam = playerData[1].split()
        team = nameAndTeam.pop(len(nameAndTeam)-1)
        name = " ".join(nameAndTeam)
        
        p = Player(name, rank, position, team)
        p.positionRank = positionRank
        p.link = link

        return p   
    
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

        filename = self.outputFilePrefix + ".md"
      
        # Create the positional ranking table
        table = CreatePositionTable(self.rankedPlayers.values())
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
            _file.write(f"{self.title}\n\n{self.description}\n\n")
            
            _file.write("## Overall Rankings\n\n")
            for player in self.rankedPlayers.values():
                _file.write(f"{player.markdown}\n")
            
            _file.write("\n\n")
            
            _file.write("## Position Ranks\n\n")
            _file.write(mdTable)
        
        return {
            "base": filename
        }


def run():
    ''' Run the web scraping for fantasy pros.
    '''
    fph = FantasyProsHockey()
    outputData = fph.run()
    
    jsonData = {}
    
    if exists("readme.json"):
        with open("readme.json", "rb") as jsonFile:
            jsonData = load(jsonFile)

    if "hockey" not in jsonData:
        jsonData["hockey"] = {}
        
        if fph.title not in jsonData["hockey"]:
            jsonData["hockey"][fph.source] = {}
            
    jsonData["hockey"][fph.source] = outputData
    
    with open("readme.json", "w") as jsonFile:
        dump(jsonData, jsonFile, indent=4)
