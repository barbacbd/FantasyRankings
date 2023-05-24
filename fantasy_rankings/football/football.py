from enum import Enum
from datetime import datetime
import pandas as pd
from ..rank import BaseRankings


class FantasyLeagueScoring(Enum):
    '''Type of scoring used for Fantasy Football League
    
    Custom scoring types are unsupported
    '''
    STD = 1
    HALF_PPR = 2
    PPR = 3


class FFRankings(BaseRankings):
    '''Base class for Fantasy Football Rankings'''

    def __init__(self, source, outputFile):
        self.source = source
        title = f"## {source} Fantasy Football Draft Rankings"
        description = (
            "The data contained in this file is the result of scraping fantasy"
            f" football draft ranking information from {source} on "
            f"{datetime.now().month}/{datetime.now().day}/{datetime.now().year}.\n\n"
            "All information contained in this file should be utilized with caution as "
            f"the rankings may change at the discretion of {source}. Information is only "
            "considered valid at the time that the information is scraped."
        )
        
        super(FFRankings, self).__init__(title, description)
        

        self.outputFilePrefix = outputFile
        
        self.rankingEndpoints = {
            FantasyLeagueScoring.STD: None,
            FantasyLeagueScoring.HALF_PPR: None,
            FantasyLeagueScoring.PPR: None
        }
        
        self.xlsxFilename = f"{outputFile}.xlsx"
        self.mdFilename   = f"{outputFile}.md"

    def run(self):
        data = {}
        
        if self.scrape():
            data["spreadsheets"] = self.saveAsXlsx()
            data["markdown"] = self.saveAsMarkdown()
        
        return data
        
    def scrape(self):
        ''' Base class does not implement this function, child Must'''
        raise NotImplementedError(f"FFRankings does not implement scrape")
        
    def saveAsXlsx(self):
        '''Save the curent data to an xlsx file'''
        
        filename = self.outputFilePrefix + ".xlsx"        
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        
        for scoringType, players in self.rankedPlayers.items():
            
            jsonData = []
            for playerData in players:
                jsonData.append(playerData.to_json())

            df = pd.DataFrame(jsonData)
            # each sheet is the type of scoring 
            sheetName = scoringType.name

            df.to_excel(writer, sheet_name=sheetName, index=False)
            
            workbook  = writer.book
            worksheet = writer.sheets[sheetName]

            (max_row, max_col) = df.shape
            worksheet.set_column(0,  max_col - 1, 12)
            worksheet.autofilter(0, 0, max_row, max_col - 1)

        # Save the file to disk
        writer.close()
        
        return filename

    def saveAsMarkdown(self):
        raise NotImplementedError("FFRankings does not implement saveAsMarkdown")

