from bs4 import BeautifulSoup as soup
from urllib2 import urlopen as uReq
from google import google
import html5lib
import pypandoc



def getHowToHeader(pagesoup):
    # Get all headers in the page
    allHeaders = pagesoup.find_all('h2')
    for header in allHeaders:
        if 'how to get' in header.string.lower():
            return header
    return False

def getPageURL(cardName):
    search_results = google.search('Duel Links GameA {} | Deck and Rulings |'.format(cardName))
    for result in search_results:
        if cardName == result.name.split(' |')[0]:
            return result.link

    return False

def getHTML(URL):
    uClient = uReq(URL)
    page_html = uClient.read()
    uClient.close()
    return page_html

def getFinalOutup(howToGet):
    # pandoc html to markdown didnt work on cases where there were multiple lines in a cell
    tableString = str(howToGet).replace('<ul>','').replace('</ul>','').replace('<li>','').replace('</li>','')
    output = pypandoc.convert_text(tableString, 'markdown_phpextra', format='html')
    # TODO: Handle mutliple lines in a cell, need to add '\n ||'
    FinalOuttup = output.replace('/c', 'http://duellinks.gamea.co/c')
    return FinalOuttup

def tableFromHeader(header):
    table = header.parent.nextSibling.contents[1].contents[0]
    return table


cardName = 'Dark Magician'
URL = getPageURL(cardName)
page_html = getHTML(URL)
page_soup = soup(page_html,'html5lib')
howToHeader = getHowToHeader(page_soup)
howToGet = tableFromHeader(howToHeader)
print getFinalOutup(howToGet)
