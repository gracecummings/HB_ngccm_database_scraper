#This is the beginning of code that scraps the ngccm database and gathers all of the characteristics of a module
#Currently, this just gathers the info one module

from lxml import etree, html
import requests
import gspread
import json
from oauth2client.client import SignedJwtAssertionCredentials
#from googleapiclient.discovery import build
#from httplib2 import Http


#Get the summary of the modules
homelink = 'http://hcal.cern.ch/ePorridge/home.py?db=HB_ngCCM_modules_2018'
homepage = requests.get(homelink)
th= html.fromstring(homepage.content)

#Initalize the list of the dictionaries that is the final output
modules = []

#Get all of the modules
templink = 'http://hcal.cern.ch/ePorridge/'
print "finding the modules"
linklist = th.xpath('//ul/*/a/@href')#uses home page to get the links of the module pages
howmany = len(linklist)

#Build some characteristic dictionaries
print "gathering the characteristics"
for k,l in enumerate(linklist):
    #Progress bar for your weary soul
    if k % 5 == 0:
        print "completed ",k

    #Initialize things and get pages
    module = {}
    link   = templink+str(l)
    page   = requests.get(link)
    t      = html.fromstring(page.content)#creates a tree of the webpage

    #Get Module Number
    h2  = t.xpath('//h2/text()')#all h2 level headers on page
    sn  = h2[1]
    snsplit = sn.split()
    num = snsplit[-1]

    #Get Module component characteristics
    module["Module Number"] = num
    chars = t.xpath('//table/tr/th/text()')
    for i,char in enumerate(chars):
        if i % 2 == 0:
            module[char] = chars[i+1]
        else:
            continue
        
    

    modules.append(module)


modules = sorted(modules, key = lambda mod:int(mod["Module Number"]))

#Update the Google Spreadsheet
#This can only be done if you have downloaded your own google API package and have set it up properly and named you json creds.json
#I found this explantion the easiest to use: https://www.makeuseof.com/tag/read-write-google-sheets-python/
#You have to turn off ad block for it though
json_key = json.load(open('creds.json'))
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope) # get email and key from creds
file = gspread.authorize(credentials) # authenticate with Google
print "opening Google Sheet (capitalized to appease our overlords)"
sheet1 = file.open("HB_Phase1_NgCCM_Location_and_Info").sheet1
#sheet2 = file.open("HB_Phase1_NgCCM_Location_and_Info").sheet2#doesn't work

#This can probably be done more elegantly (and maybe faster?) and using batch mode
sheet1.update_cell(1,1,'Module Number')
sheet1.update_cell(1,2,'Status')
sheet1.update_cell(1,3,'Location')
sheet1.update_cell(1,4,'Clk Card SN')
sheet1.update_cell(1,5,'M Ctrl Card SN')
sheet1.update_cell(1,6,'S Ctrl Card SN')
#sheet2.update_cell(1,1,'Clk Card SN')
#sheet2.update_cell(1,2,'1Wire ID')

print "filling Google Sheet"
for i,m in enumerate(modules):
    #Again, a progress bar
    if i % 5 == 0:
        print "Updated sheet with {0} modules".format(i)
    if "Module Number" in m:
        sheet1.update_cell(i+2,1,m["Module Number"])
    #sheet1.update_cell(i+2,2,m["status"]#not avaiable yet
    #sheet1.update_cell(i+2,3,m["location"]#not avaible yet
    if "Clock Board SN" in m:
        sheet1.update_cell(i+2,4,m["Clock Board SN"])
    if "Primary Control Board SN" in m:
        sheet1.update_cell(i+2,5,m["Primary Control Board SN"])
    if "Secondary Control Board SN" in m:
        sheet1.update_cell(i+2,6,m["Secondary Control Board SN"])
    #sheet2.update_cell(i+2,1,m["Clock Board SN"])
    #sheet2.update_cell(i+2,2,m["Cloack Board 1Wire ID"])

print "Enjoy your Google Sheet"
