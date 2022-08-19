import requests
from bs4 import BeautifulSoup
from .baseball import FBRankings
from ..player import Player
from collections import defaultdict
from json import dump, load
from os.path import exists
import re


class FantasyProsBaseball(FBRankings):

    '''Class to scrape all fantasy baseball draft information from Fantasy Pros'''
    
    TableFields = [
        'Rank',
        'Player/Team',
        'Best',
        'Worst',
        'Average',
        'STDDev',
        'ADP',
        'vs. ADP'
    ]
    
    def __init__(self):
        super(FantasyProsBaseball, self).__init__("Fantasy Pros", "FantasyProsBaseballDraft")
        self.outputFile = "FantasyProsBaseballDraft"
        self.baseWebpage = "https://www.fantasypros.com"
        
        self.rankingsPage = "/mlb/rankings/overall.php"
        
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
            
            if len(_tds) < len(FantasyProsBaseball.TableFields):
                print(_tds)
                print("Number of player elements does not match the known fields")
                continue
            else:
                # Baseball threw in a few extra data points that show up
                # but are not displayed on the web page
                _tds = _tds[:len(FantasyProsBaseball.TableFields)]
            
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
    fph = FantasyProsBaseball()
    outputData = fph.run()
    
    jsonData = {}
    
    if exists("readme.json"):
        with open("readme.json", "rb") as jsonFile:
            jsonData = load(jsonFile)

    if "baseball" not in jsonData:
        jsonData["baseball"] = {}
        
        if fph.title not in jsonData["baseball"]:
            jsonData["baseball"][fph.source] = {}
            
    jsonData["baseball"][fph.source] = outputData
    
    with open("readme.json", "w") as jsonFile:
        dump(jsonData, jsonFile, indent=4)
