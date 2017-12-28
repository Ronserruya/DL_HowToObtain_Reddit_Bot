from bs4 import BeautifulSoup as soup
from urllib2 import urlopen as uReq
from google import google
import html5lib
import pypandoc
import time
import praw
import config
import re

def bot_login():
    # Login with praw
    print "Logging in..."
    r = praw.Reddit(username = config.username,
                    password= config.password,
                    client_id = config.client_id,
                    client_secret = config.client_secret,
                    user_agent = "Duel Links How to obtain bot")
    print "Logged in!"

    return r

def getRelevantComments(r,lastReply):
    # Get comments in </r/DuelLinks> that has any string between " {} "
    # eg. bla bla bla {Blast held by a tribute}
    relevantComments = []

    print "Obtaining last 20 comments..."
    # Go over the last 20 comments
    for comment in r.subreddit('DuelLinks').comments(limit=20):
        if comment.created_utc > lastReply and \
                        comment.author.name != 'YugiohLinkBot' and comment.author.name != config.username:
            relevantComments.append(comment)

    return relevantComments

def replyToComment(comment,msg):
    commentFormat = '\n\n ______________________________________ \n\n' \
                    '^(I AM A BOT, use {cardname} or {{cardname}} to call me.  \n ' \
                    'The info for this comment was extracted from: ' \
                    'duellinks.gamea.co , I don\'t have any relation to that site.)    \n' \
                    '[Source Code](https://github.com/Ronserruya/DL_HowToObtain_Reddit_Bot) '
    comment.reply(msg + commentFormat)
    return comment.created_utc

def getHowToHeader(pagesoup):
    # Get all headers in the page
    allHeaders = pagesoup.find_all('h2')
    #Get the header that has "how to get"
    for header in allHeaders:
        if 'how to get' in header.string.lower():
            return header
    return False

def getPageURL(cardName):
    #Search the card name on google,and return its gameA link
    time.sleep(5)
    search_results = google.search('Duel Links GameA {} | Deck and Rulings |'.format(cardName))
    for result in search_results:
        #If someone inputs "Blue eyes", I want it to still find "Blue-Eyes"
        if cardName.lower().replace('-',' ') == result.name.lower().replace('-',' ').split(' |')[0]:
            return result.link
    return False

def getHTML(URL):
    #Get the HTML of the gameA page
    uClient = uReq(URL)
    page_html = uClient.read()
    uClient.close()
    return page_html

def getFinalOutup(howToGet):
    # pandoc html to markdown didn't work on some cases, so I try to edit the html to make it work
    tableString = str(howToGet).replace('<ul>','').replace('</ul>','').\
        replace('<li>','%| | ').replace('</li>','|').replace('<br/>','')
    #Markdown_phpextra is similar to reddit's formatting
    output = pypandoc.convert_text(tableString, 'markdown_phpextra', format='html')
    FinalOuttup = output.replace('/c', 'http://duellinks.gamea.co/c').replace('%','\n')
    return FinalOuttup

def tableFromHeader(header):
    #Navigate from "How to get" header to the following table
    table = header.parent.nextSibling.contents[1].contents[0]
    return table

def run_bot(r,lastReply):
    relevantComments = getRelevantComments(r,lastReply)
    if len(relevantComments) == 0:
        print 'No relevant comments'
        return lastReply

    for comment in relevantComments:
        try:
            cardName = re.search('(?<=\{)(.*?)(?=\})',comment.body).group(0).replace('{','').replace('}','')
        except Exception as e:
            continue

        URL = getPageURL(cardName)
        if URL == False:
            lastReply = replyToComment(comment,'Sorry, but I was not able to find this card')
            continue

        page_html = getHTML(URL)
        page_soup = soup(page_html, 'html5lib')
        howToHeader = getHowToHeader(page_soup)
        if howToHeader == False:
            lastReply = replyToComment(comment,'Sorry, I was not able to find the How To get Info,'
                                   ' but this is the link to the card\'s page: {}'.format(URL))
            continue

        howToGet = tableFromHeader(howToHeader)
        FinalOutput = getFinalOutup(howToGet)
        if 'under construction.' in FinalOutput.lower():
            lastReply = replyToComment(comment, 'Sorry, I was not able to find the How To get Info,'
                                                ' but this is the link to the card\'s page: {}'.format(URL))
            continue

        lastReply = replyToComment(comment,FinalOutput)

    return lastReply


    return True


def main():
    startTime = time.time() #Current UNIX time

    r = bot_login()
    while True:
        # startTime gets the time of the last comment I replied to
        startTime = run_bot(r,startTime)
        print "Waiting for 30 seconds"
        time.sleep(30)



if __name__ == '__main__':
    main()

