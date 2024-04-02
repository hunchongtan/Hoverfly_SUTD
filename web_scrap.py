import requests
from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords
stopwords = stopwords.words('english')

"""user inputs"""
url = "https://en.wikipedia.org/wiki/Pico_4"

"""scrape page"""
response = requests.get(url=url, )
soup = BeautifulSoup(response.content, 'html.parser')

"""get title"""
title = soup.find(id="firstHeading")
print(title.string)

"""get text"""
text = soup.find(id="bodyContent").find_all("p")
print(text)