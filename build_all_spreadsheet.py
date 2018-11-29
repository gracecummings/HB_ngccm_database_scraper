#This is the script that you will run to build the spreadsheet of the cards
from lxml import etree, html
import HB_database_scraper
import requests
from google.oauth2 import service_account
import googleapiclient.discovery

if __name__=='__main__':
    #Access database homepage to find all the modules
    homelinkmod           = 'http://hcal.cern.ch/ePorridge/home.py?db=HB_ngCCM_modules_2018'
    homelinkclk           = 'http://hcal.cern.ch/ePorridge/home.py?db=HB_ngCCM_clocks_2018'
    homelinkctrl          = 'http://hcal.cern.ch/ePorridge/home.py?db=HB_ngCCM_cntrls_2018'
    modlinklist,nummods   = HB_database_scraper.accessFromHomepage(homelinkmod)
    clklinklist,numclks   = HB_database_scraper.accessFromHomepage(homelinkclk)
    ctrllinklist,numctrls = HB_database_scraper.accessFromHomepage(homelinkctrl)

    #Gathering characteristics
    templatelink = 'http://hcal.cern.ch/ePorridge/'

    #Building module characteristic dictionaries
    print "Gathering the module characteristics"
    modules = []
    for k,l in enumerate(modlinklist):
        #Progress bar
        if k % 5 == 0:
            print "    completed ",k

        #Accessing webpage for each module
        module = {}
        t = HB_database_scraper.buildHTMLTree(templatelink,l)

        #Filling a dictionary for each module
        module["Module Number"] = HB_database_scraper.moduleNumber(t)
        HB_database_scraper.moduleCharFill(t,module)#Fills a dictionary for with characteristic
        modules.append(module)

    #Building clk card dictionaries
    print "Gathering clk card characteristics"
    clks = []
    for k,l in enumerate(clklinklist):
        if k % 5 == 0:
            print "    completed ",k

        clkcard = {}
        t = HB_database_scraper.buildHTMLTree(templatelink,l)
        clkcard["Clk Card Number"] = HB_database_scraper.moduleNumber(t)
        clkcard["Factory SN"]      = HB_database_scraper.getClkFactorySN(t)
        HB_database_scraper.get1Wire("Clock Board 1Wire ID","Clk Card Number","Clock Board SN",modules, clkcard)

        #Checking which Module it is within
        HB_database_scraper.getWhichModule("Clock Board SN","Clk Card Number",modules,clkcard)
        clks.append(clkcard)                
    
    #Building cntrl card dictionaries
    print "Gatering Control Card characteristics"
    ctrls = []
    for k,l in enumerate(ctrllinklist):
        if k % 5 == 0:
            print "    completed ",k

        ctrlcard = {}
        t = HB_database_scraper.buildHTMLTree(templatelink,l)
        ctrlcard["Ctrl Card Number"] = HB_database_scraper.moduleNumber(t)
        if int(ctrlcard["Ctrl Card Number"]) < 100:#We have a few clearly incorrect SN in database
            continue
        ctrlcard["Factory SN"] = HB_database_scraper.getCtrlFactorySN(t)
        HB_database_scraper.getModuleInfo(modules,ctrlcard)
        if "Is Primary" in ctrlcard:
            if ctrlcard["Is Primary"] == 0:
                HB_database_scraper.get1Wire("Secondary Control Board 1Wire ID","Ctrl Card Number","Secondary Control Board SN",modules,ctrlcard)
            elif ctrlcard["Is Primary"] == 1:
                HB_database_scraper.get1Wire("Primary Control Board 1Wire ID","Ctrl Card Number","Primary Control Board SN",modules,ctrlcard)
        else:
            ctrlcard["1 Wire"] = "not yet accessed"

        ctrls.append(ctrlcard)

    #Preparing the information for spreadsheet upload
    modules      = sorted(modules, key = lambda mod:int(mod["Module Number"]))
    modchars     = HB_database_scraper.totalKeys(modules)#Returns maximal key list
    sortmodchars = HB_database_scraper.charSorterMod(modchars)
    clks         = sorted(clks, key = lambda clk:int(clk["Clk Card Number"]))
    clkchars     = HB_database_scraper.totalKeys(clks)
    sortedclk    = HB_database_scraper.charSorterClk(clkchars)
    ctrls        = sorted(ctrls, key = lambda ctrl:int(ctrl["Ctrl Card Number"]))
    ctrlchars    = HB_database_scraper.totalKeys(ctrls)
    sortedctrl   = HB_database_scraper.charSorterCtrl(ctrlchars) 
    
    #What will be written to the sheet
    values = []
    values.append(sortmodchars)#This will be the header
    HB_database_scraper.makeValueList(values,modules,sortmodchars)
    sheetrange = HB_database_scraper.sheetRangeFinder(modules,sortmodchars,"Assembled NgCCM Modules")#Name of google sheet tab that I already made

    values1 = []
    values1.append(sortedclk)
    HB_database_scraper.makeValueList(values1,clks,sortedclk)
    sheet1range = HB_database_scraper.sheetRangeFinder(clks,sortedclk,"Prod 3 Clk Cards")

    values2 = []
    values2.append(sortedctrl)
    HB_database_scraper.makeValueList(values2,ctrls,sortedctrl)
    sheet2range = HB_database_scraper.sheetRangeFinder(ctrls,sortedctrl,"Prod 3 Ctrl Cards")    
    
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
    data1 = [{'range':sheet1range,'values':values1}]
    body1 = {'valueInputOption':'RAW','data':data1}
    result1 = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID,body=body1).execute()
    data2 = [{'range':sheet2range,'values':values2}]
    body2 = {'valueInputOption':'RAW','data':data2}
    result2 = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID,body=body2).execute()
    print "Google doc updated, check it out"
    
