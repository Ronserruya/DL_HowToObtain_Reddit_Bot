# DL_HowToObtain_Reddit_Bot

Reddit bot that web scrapes "http://duellinks.gamea.co/" and tells the user how to get a specific card in the video game "Yugioh - Duel Links"

## Usage

On the subbreddit [/r/DuelLinks](https://www.reddit.com/r/DuelLinks/), comment any card name between two curled braces, and the bot will answer. (Example in screenshots)

## Prerequisites

Developed on Python 2.7.12

Needed dependeices are all in the "requirments.txt" file  
Use this to install them
```
pip install -r requirments.txt  
```  
In addition to these python packeges, [Pandoc](http://pandoc.org/installing.html) is also needed

## Built With

* [PRAW](https://github.com/praw-dev/praw) - Used to interact with the reddit API
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Used for web scraping
* [html5lib](https://github.com/html5lib/html5lib-python) - Used to parse the web page
* [pyPandoc](https://github.com/bebraw/pypandoc) - Used to convert HTML to Markdown
* [Google-Search-API](https://github.com/abenassi/Google-Search-API) - Used to search for the cards on http://duellinks.gamea.co/


## Authors

* **Ron Serruya** - *Initial work* - [Ronserruya](https://github.com/Ronserruya)

## Screenshots

![alt text](Screenshots/DLScreenshot.png)

