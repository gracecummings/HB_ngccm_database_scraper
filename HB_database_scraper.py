#These are the functions that are used to scrap the 2018 ngccm HB database
#Written by Grace E. Cummings, 20 11 2018

from lxml import html

def moduleNumber(htmltree,moduledict):
    h2  = htmltree.xpath('//h2/text()')#all h2 level headers on page
    sn = h2[1]
    snsplit = sn.split()
    num = snsplit[-1]
    moduledict["Module Number"] = num

def moduleChars(htmltree,moduledict):
    chars = t.xpath('//table/tr/th/text()')
    for i,char in enumerate(chars):
        if i % 2 == 0:
            moduledict[char] = chars[i+1]
        else:
            continue
