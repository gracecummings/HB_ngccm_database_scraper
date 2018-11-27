#This is the script that you will run to build the spreadsheet of the cards
from lxml import etree, html
import HB_database_scraper
import requests
from google.oauth2 import service_account
import googleapiclient.discovery

if __name__=='__main__':
    #Access database homepage to find all the modules
    homelink = 'http://hcal.cern.ch/ePorridge/home.py?db=HB_ngCCM_modules_2018'
    homepage = requests.get(homelink)
    th = html.fromstring(homepage.content)

    #Building framework to access each module's page
    print "Finding the module hyperlinks"
    templatelink = 'http://hcal.cern.ch/ePorridge/'
    linklist = th.xpath('//ul/*/a/@href')#list of each module link
    nummods  = len(linklist)

    #Building module characteristic dictionaries
    print "Gathering the module characteristics"
    modules = []
    for k,l in enumerate(linklist):
        #Progress bar
        if k % 5 == 0:
            print "    completed ",k

        #Accessing webpage for each module
        module = {}
        link   = templatelink+str(l)
        page   = requests.get(link)
        t = html.fromstring(page.content)#creates a tree of the webpage

        #Filling a dictionary for each module
        module["Module Number"] = HB_database_scraper.moduleNumber(t)
        HB_database_scraper.moduleCharFill(t,module)#Fills a dictionary for with characteristic
        modules.append(module)

    #Preparing the information for spreadsheet upload
    modules  = sorted(modules, key = lambda mod:int(mod["Module Number"]))
    modchars = HB_database_scraper.totalKeys(modules)#Returns maximal key list
    sortmodchars = HB_database_scraper.charSorter(modchars)
    
    #What will be written to the sheet
    values = []
    values.append(sortmodchars)#This will be the header
    for mod in modules:
        row = []
        for key in sortmodchars:
            if key in mod:
                row.append(mod[key])
            else:
                row.append("n/a")
        values.append(row)
    sheetrange = HB_database_scraper.sheetRangeFinder(modules,sortmodchars,"Sheet1")#Name of google sheet tab that I already made

    #Google Credentials and uploading
    print "Starting the Google Credential Authorization" 
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'phase1upgrade_cred2.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)#first argument is the API you want to use
    sheet = service.spreadsheets()
    SPREADSHEET_ID = '1nE30FxWRhQVw_89h6eNmQjSEmHBZQp_GBM_8ey9LY5A'#In URL of the page you want
    data = [{'range':sheetrange,'values':values}]
    body = {'valueInputOption':'RAW','data':data}
    result = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID,body=body).execute()

