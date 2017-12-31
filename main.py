from bs4 import BeautifulSoup as soup
from urllib2 import urlopen
from google import google
import html5lib
import pypandoc
import time
import praw
import config
import re
import string

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

def getRelevantComments(r,startTime):
    # Get comments in </r/DuelLinks> that are not from me or from YugiohLinkBot , since he comments with {*} as well
    relevantComments = []

    #print "Obtaining last 20 comments..."
    # Go over the last 20 comments
    for comment in r.subreddit('DuelLinks').comments(limit=20):
        if comment.created_utc > startTime and \
                        comment.author.name != 'YugiohLinkBot' and comment.author.name != config.username:
            relevantComments.append(comment)

    return relevantComments,time.time()

def replyToComment(comment,msg,url = 'duellinks.gamea.co ,'):
    commentFormat = '\n\n ______________________________________ \n\n' \
                    '^(I AM A BOT, use {cardname} or {{cardname}} to call me.  \n ' \
                    'The info for this comment was extracted from: ' +  \
                    url +'I don\'t have any relation to that site.)    \n' \
                    '[Source Code](https://github.com/Ronserruya/DL_HowToObtain_Reddit_Bot)  \n\n' \
                    '[Strawpoll about this bot](http://www.strawpoll.me/14720346)'
    comment.reply(msg + commentFormat)

def getHowToHeader(pagesoup):
    # Get all headers in the page
    allHeaders = pagesoup.find_all('h2')
    #Get the header that has "how to get"
    for header in allHeaders:
        if 'how to get' in header.string.lower():
            return header
    return False

def getPageURL(cardName):
    # Search the card name on google,and return its gamea link
    # Example title: Dark Magician | Deck and Rulings | YuGiOh! Duel Links - GameA
    # Sleep to prevent google blocking
    time.sleep(5)
    search_results = google.search('Duel Links GameA {} | Deck and Rulings |'.format(cardName))
    if search_results == None: # If google blocked the request
        return 'CAPTCHA'

    for result in search_results:
        #Try to fix misspelling
        if cardName.lower().replace('-',' ').replace(',','').replace('\'','').replace(':','') == \
                result.name.lower().replace('-',' ').replace(',','').replace('\'','').replace(':','').split(' | d')[0]:
            return result.link

    time.sleep(5)
    search_results = google.search('Duel Links GameA {} | Deck and Tips |'.format(cardName))
    if search_results == None: # If google blocked the request
        return 'CAPTCHA'

    for result in search_results:
        if cardName.lower().replace('-', ' ').replace(',','').replace('\'','') == \
                result.name.lower().replace('-', ' ').replace(',','').replace('\'','').split(' | D')[0]:
            return result.link
    return False

def getHTML(URL):
    #Get the HTML of the gameA page
    uClient = urlopen(URL)
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

def reportError(r,comment,cardname,message):
    errorMsg = '{} Error report:  \n\n' \
               'Comment: {}  \n\n' \
               'Cardname: {}  \n\n' \
               'Error: {}'.format(config.username,comment.permalink,cardname,message)
    r.redditor(config.developer).message('{} Error report'.format(config.username),errorMsg)

def run_bot(r,startTime):
    relevantComments,startTime = getRelevantComments(r,startTime)
    if len(relevantComments) == 0:
        #print 'No relevant comments'
        return startTime

    for comment in relevantComments:
        #Get any string between {} , e.g {Time Wizard}, continue to next comment if not found

        cards = re.findall('(?<=\{)(.*?)(?=\})',comment.body)
        commentOutput = ''
        urlOutput = ''
        for cardName in cards:
            cardName = cardName.replace('{','').replace('}','')

            try:
                URL = '          ' #Reset URL value, so it wont remove the first card in a case of an error
                commentOutput += '**'+string.capwords(cardName) + ':**  \n\n'
                if cardName == 'fail':
                    a = 5/0
                URL = getPageURL(cardName)
                if URL == 'CAPTCHA':
                    reportError(r,comment,cardName,'Got CAPTCHA')
                    time.sleep(900) #Sleep for 15 mins, for google captcha to disappear
                    return time.time() #return the excpected startTime
                if URL == False:
                    commentOutput += 'Sorry, but I was not able to find this card.  \n'
                    continue
                urlOutput += URL + ' ,'

                page_html = getHTML(URL)
                page_soup = soup(page_html, 'html5lib')
                howToHeader = getHowToHeader(page_soup)
                if howToHeader == False:
                    commentOutput += 'Sorry, I was not able to find the How To get Info,' \
                                     ' but this is the link to the card\'s page: {}  \n'.format(URL)
                    continue

                howToGet = tableFromHeader(howToHeader)
                FinalOutput = getFinalOutup(howToGet)
                if 'under construction.' in FinalOutput.lower():
                    commentOutput += 'Sorry, I was not able to find the How To get Info,' \
                                     ' but this is the link to the card\'s page: {}  \n'.format(URL)
                    continue

                commentOutput += FinalOutput + '  \n'
            except Exception as e:
                reportError(r, comment, cardName, e.message)
                commentOutput = commentOutput.replace('**'+string.capwords(cardName) + ':**  \n\n','')
                urlOutput = urlOutput.replace(URL + ' ,','')

        if commentOutput != '': # If there is anything to comment
            if urlOutput == '': # If you have no URL to show
                replyToComment(comment, commentOutput)
            else: # If you have a URL to show
                replyToComment(comment,commentOutput,urlOutput)



    return startTime



def main():
    startTime = time.time() #Current UNIX time

    r = bot_login()
    while True:
        # startTime gets the last time I went over the comments
        startTime = run_bot(r,startTime)
        #print "Waiting for 30 seconds"
        time.sleep(30)



if __name__ == '__main__':
    main()

