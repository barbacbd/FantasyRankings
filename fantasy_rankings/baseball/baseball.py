from datetime import datetime
import pandas as pd
from ..rank import BaseRankings


class FBRankings(BaseRankings):
    '''Base class for Fantasy Baseball Rankings'''

    def __init__(self, source, outputFile):
        self.source = source
        title = f"## {source} Fantasy Baseball Draft Rankings"
        description = (
            "The data contained in this file is the result of scraping fantasy"
            f" baseball draft ranking information from {source} on "
            f"{datetime.now().month}/{datetime.now().day}/{datetime.now().year}.\n\n"
            "All information contained in this file should be utilized with caution as "
            f"the rankings may change at the discretion of {source}. Information is only "
            "considered valid at the time that the information is scraped."
        )
        
        super(FBRankings, self).__init__(title, description)
        

        self.outputFilePrefix = outputFile
        
        self.rankingEndpoints = {
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
        raise NotImplementedError(f"FBRankings does not implement scrape")
        
    def saveAsXlsx(self):
        '''Save the curent data to an xlsx file'''
        
        writer = pd.ExcelWriter(self.xlsxFilename, engine='xlsxwriter')
        
        jsonData = []
        for k, playerData in self.rankedPlayers.items():
            jsonData.append(playerData.to_json())
            
        df = pd.DataFrame(jsonData)
        df.to_excel(writer, sheet_name='draft', index=False)
        workbook  = writer.book
        worksheet = writer.sheets['draft']

        (max_row, max_col) = df.shape
        worksheet.set_column(0,  max_col - 1, 12)
        worksheet.autofilter(0, 0, max_row, max_col - 1)

        # Save the file to disk
        writer.save()

        return self.xlsxFilename

    def saveAsMarkdown(self):
        raise NotImplementedError("FBRankings does not implement saveAsMarkdown")

