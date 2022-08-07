from json import load
from os.path import dirname, abspath, join


def readJsonAddToReadme():
    '''Update the base README found in templates. This file will 
    replace the readme with any updated information when the 
    data is scraped online.
    '''
    jsonData = {}
    
    with open("readme.json", "rb") as jsonFile:
        jsonData = load(jsonFile)
    
    sportsData = ""
    
    for sport, sportData in jsonData.items():
        sportsData += f"## {sport}\n\n"
        
        for source, sourceData in sportData.items():
            sportsData += f'- [{source}](./docs/{sourceData["markdown"]["base"]})'

        # Add extra space for each sport 
        sportsData += "\n\n"

    
    with open(join(dirname(abspath(__file__)), "templates/README.md.template"), "rb") as j2File:
        template = j2File.read().decode('utf-8')

    template += "\n\n" + sportsData

    with open("README.md", "w+") as j2File:
        j2File.write(template)

    
