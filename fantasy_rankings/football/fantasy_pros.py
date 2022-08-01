import requests
from bs4 import BeautifulSoup
from .football import FFPlayer, FFRankings, FantasyLeagueScoring
from collections import defaultdict


class FantasyProsFootball(FFRankings):

    '''Class to scrape all fantasy football draft information from Fantasy Pros'''
    
    def __init__(self):
        super(FantasyProsFootball, self).__init__("Fantasy Pros", "FantasyProsFootballDraft")
        self.outputFile = "FantasyProsFootballDraft"
        self.baseWebpage = "https://www.fantasypros.com"
        
        self.rankingEndpoints[FantasyLeagueScoring.STD] = "/nfl/cheatsheets/top-players.php"
        self.rankingEndpoints[FantasyLeagueScoring.PPR] = "/nfl/cheatsheets/top-half-ppr-players.php"
        self.rankingEndpoints[FantasyLeagueScoring.PPR] = "/nfl/cheatsheets/top-ppr-players.php"
        
        self.playerEndpoints = defaultdict(list)

    def run(self):
        if self.scrape():
            self.saveAsXlsx()
            self.saveAsMarkdown()

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

    def _positionRankings(self):
        '''Create the rankings by position.'''

    def mdBody(self):
        body = "## Fantasy Pros Player Rankings\n\n"
        for player in self.rankedPlayers:
            body += f"{player.asMarkdown()}\n"
        return body

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
        
        return FFPlayer(name, rank, position, teamCode)