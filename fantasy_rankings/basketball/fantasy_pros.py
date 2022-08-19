import requests
from bs4 import BeautifulSoup
from .basketball import FBRankings
from ..player import Player, CreatePositionTable, AdjustTableToMarkdown
from collections import defaultdict
from json import dump, load
from os.path import exists
import re


class FantasyProsBasketball(FBRankings):

    '''Class to scrape all fantasy basketball draft information from Fantasy Pros'''
    
    TableFields = [
        'Rank',
        'Player/Team',
        'Best',
        'Worst',
        'Avgerage',
        'STDDev'
    ]
    
    def __init__(self):
        super(FantasyProsBasketball, self).__init__("Fantasy Pros", "FantasyProsBasketballDraft")
        self.outputFile = "FantasyProsBasketballDraft"
        self.baseWebpage = "https://www.fantasypros.com"
        
        self.rankingsPage = "/nba/rankings/overall.php"
        
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
        for i, tr in enumerate(playerData.find_all("tr")):
            tds = tr.find_all('td')
            _tds = [td.text for td in tds]
            
            if len(_tds) != len(FantasyProsBasketball.TableFields):
                print("Number of player elements does not match the known fields")
                continue
            
            for td in tds:
                a = td.find('a')
                if a:
                    if a.get('href'):
                        links.append(a.get('href'))
            
            data.append(_tds)
        
        if len(data) == 0:
            print("Found no data")
            return False
        
        if len(data) != len(links):
            print(f"Number of players does not match player links: {len(data)} != {len(links)}")
            return False
        
        self.rankedPlayers.clear()
        for i, pd in enumerate(data):
            p = self._createPlayer(pd)
            link = links[i]
            p.link = self.baseWebpage + "".join(link.split())
            self.rankedPlayers[p.rank] = p

        return True
    
    def _createPlayer(self, playerData):
        rank = int(playerData[0])
        
        throwOutEnd = playerData[1].find(')') < len(playerData[1]) - 2
        
        # parse the player name, team, and position
        playerInfo = playerData[1].replace("(", "").replace(")", "").replace("-", "")
        playerInfo = playerInfo.split()
        
        if throwOutEnd:
            playerInfo.pop(len(playerInfo)-1)
        
        position = playerInfo.pop(len(playerInfo)-1)
        team = playerInfo.pop(len(playerInfo)-1)
        name = " ".join(playerInfo)
         
        p = Player(name, rank, position, team)
        return p   
    
    def saveAsMarkdown(self):
        filename = self.outputFilePrefix + ".md"
              
        with open(filename, "w+") as _file:
            _file.write(f"{self.title}\n\n{self.description}\n\n")
            
            _file.write("## Spreadsheet\n\n")
            _file.write(f"- [{self.source}]({self.outputFilePrefix}.xlsx)\n\n")
            
            _file.write("## Overall Rankings\n\n")
            for player in self.rankedPlayers.values():
                _file.write(f"{player.markdown}\n")
            
            _file.write("\n\n")
            
        
        return {
            "base": filename
        }


def run():
    ''' Run the web scraping for fantasy pros.
    '''
    fph = FantasyProsBasketball()
    outputData = fph.run()
    
    jsonData = {}
    
    if exists("readme.json"):
        with open("readme.json", "rb") as jsonFile:
            jsonData = load(jsonFile)

    if "basketball" not in jsonData:
        jsonData["basketball"] = {}
        
        if fph.title not in jsonData["basketball"]:
            jsonData["basketball"][fph.source] = {}
            
    jsonData["basketball"][fph.source] = outputData
    
    with open("readme.json", "w") as jsonFile:
        dump(jsonData, jsonFile, indent=4)
