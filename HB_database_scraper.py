#These are the functions that are used to scrap the 2018 ngccm HB database
#Written by Grace E. Cummings, 20 11 2018

from lxml import html
import string

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
    
def charSorter(listkeys):
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

