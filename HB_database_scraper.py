#These are the functions that are used to scrap the 2018 ngccm HB database
#Written by Grace E. Cummings, 20 11 2018

from lxml import html
import string
import requests

def accessFromHomepage(homelink):
    homepage = requests.get(homelink)
    t = html.fromstring(homepage.content)
    print "Gathering Links"
    linklist = t.xpath('//ul/*/a/@href')#list of each compoent's link after base link supplied in main script
    numcomp = len(linklist)
    return linklist,numcomp    

def buildHTMLTree(templatelink,linktext):
    link = templatelink+str(linktext)
    page = requests.get(link)
    t = html.fromstring(page.content)
    return t

def moduleNumber(htmltree):
    h2  = htmltree.xpath('//h2/text()')#all h2 level headers on page
    sn = h2[1]
    snsplit = sn.split()
    num = snsplit[-1]
    return  num

def moduleCharFill(htmltree,moduledict):
    chars = htmltree.xpath('//table/tr/th/text()')
    for i,char in enumerate(chars):
        if i % 2 == 0:
            moduledict[char] = chars[i+1]
        else:
            continue
        
def getClkFactorySN(htmltree):
    td = htmltree.xpath('//td/text()')#This can be made better
    snentry = td[5]
    snparts = snentry.split("AMTI:")
    if len(snparts) > 1:
        sn = snparts[1]
    else:
        snpart2 = snparts[0].split(": ")
        sn = snpart2[1]
    return sn

def getCtrlFactorySN(htmltree):
    td = htmltree.xpath('//td/text()')#This can be made better
    snentry = td[5]
    listsnent = snentry.split("AMTI:")
    if len(listsnent) > 1:
        sn = listsnent[1]
    else:
        l2 = listsnent[0].split(" ")
        sn = l2[-1]
    return sn

def getWhichModule(modkey,cardkey,modules,card):
    for mod in modules:
        if modkey in mod:
            if card[cardkey] in mod[modkey]:
                card["NgCCM Module"] = mod["Module Number"]

    if "NgCCM Module" not in card:
        card["NgCCM Module"] = "not installed"

def get1Wire(needkey,cardkey,modkey,modules,card):
    for mod in modules:
        if needkey in mod:
            if card[cardkey] in mod[modkey]:
                card["1 Wire"] = mod[needkey]

    if "1 Wire" not in card:
        card["1 Wire"] = "not yet associated"

def getModuleInfo(modules,card):
    for mod in modules:
        if "Primary Control Board SN" in mod:
            if card["Ctrl Card Number"] in mod["Primary Control Board SN"]:
                card["NgCCM Module"] = mod["Module Number"]
                card["Is Primary"] = 1
        if "Secondary Control Board SN" in mod:
            if card["Ctrl Card Number"] in mod["Secondary Control Board SN"]:
                card["NgCCM Module"] = mod["Module Number"]
                card["Is Primary"] = 0
        
    if "NgCCM Module" not in card:
        card["NgCCM Module"] = "not installed"
            
def totalKeys(modulelist):
    exampledict = max(modulelist)
    keys = exampledict.keys()
    return keys

def sheetRangeFinder(modulelist,keylist,sheetname):
    numletter  = list(string.ascii_uppercase)
    numentries = len(modulelist)
    numkeys    = len(keylist)
    letterrange = numletter[numkeys - 1]
    rangesheet  = sheetname+'!A1:'+letterrange+str(numentries+2)
    return rangesheet
    
def charSorterMod(listkeys):
    l = listkeys
    l2 = []
    for char in l:
        if "Module Number" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "Clock Board SN" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "Primary Control Board SN" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "Secondary Control Board SN" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "Clock Board 1Wire ID" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "Primary Control Board 1Wire ID" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "Secondary Control Board 1Wire ID" in char:
            l2.append(char)
            l.remove(char)
    l3 = l2+l
    return l3

def charSorterClk(listkeys):
    l = listkeys
    l2 = []
    for char in l:
        if "Clk Card Number" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "1 Wire" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "Factory SN" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "NgCCM Module" in char:
            l2.append(char)
            l.remove(char)
    return l2

def charSorterCtrl(listkeys):
    l = listkeys
    l2 = []
    for char in l:
        if "Ctrl Card Number" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "1 Wire" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "Factory SN" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "NgCCM Module" in char:
            l2.append(char)
            l.remove(char)
    for char in l:
        if "Is Primary" in char:
            l2.append(char)
            l.remove(char)
    return l2

def makeValueList(valuelist,objs,sortedobjs):
    for obj in objs:
        row = []
        for key in sortedobjs:
            if key in obj:
                row.append(obj[key])
            else:
                row.append("n/a")
        valuelist.append(row)
    
