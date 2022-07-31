import requests
from bs4 import BeautifulSoup
from enum import Enum
from datetime import datetime
import pandas as pd
from .football import FFPlayer, FFRankings


class FantasyProsFootball(FFRankings):

    '''Class to scrape all fantasy football draft information from Fantasy Pros'''

    Title = '''Fantasy Pros Fantasy Football Draft Rankings'''
    Description = f'''
    The data contained in this file is the result of scraping fantasy football draft ranking information
    from Fantasy Pros on {datetime.now().month}/{datetime.now().day/{datetime.now().year}. 
    
    All information contained in this file should be utilized with caution as the rankings may change
    at the discretion of Fantasy Pros. Information is only considered valid at the time that the 
    information is scraped. 
    '''
    
    def __init__(self):
        super(FantasyProsFootball, self).__init__("FantasyProsFootballDraft")
        self.outputFile = "FantasyProsFootballDraft"
        self.baseWebpage = "https://www.fantasypros.com/nfl/"
        self._draftEndpoint = "cheatsheets/top-ppr-players.php"
        self.playerEndpoints = {}

    def run(self):
        if self.scrape():
            self.saveAsXlsx()
            self.saveAsMarkdown()

    def scrape(self) -> bool:
        '''Scrape the data from the draft rankings endpoint.
        Set the Draft ranking information to this instance.
        
        :return: True on success
        '''
        site = self.baseWebpage + self._draftEndpoint
        webpage = requests.get(site)
        page_html = BeautifulSoup(webpage.text, 'html.parser')

        playerListDivs = page_html.find_all("div", {"class": "player-list"})
        if 0 > len(playerListDivs) > 1:
            return False

        playerListDiv = playerListDivs[0]

        self.rankedPlayers.clear()
        for ul in playerListDiv.find_all('ul'):
            liDataAsPlayers = []
            for li in ul.find_all('li'):
                liDataAsPlayers.append(FFPlayer(li.text.replace(u'\xa0', u' ')))
            self.rankedPlayers.extend(liDataAsPlayers)

        return True
