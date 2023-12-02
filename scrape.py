'''
use bs4 to scrape a given link and any specific parts of the soup
'''
from bs4 import BeautifulSoup
import requests

scrapes = {}    #url: scrape-object

class Scrape:
    def __init__(self, soupe=None, text=None):
        self.soup = None
        self.text = None
    
    def get_soup(self):
        return self.soup
    
    def get_text(self):
        return self.text
    
    def set_soup(self, soup):
        if self.soup != None:
            raise Exception("Attempting to reset soup")
        self.soup = soup
    
    def set_text(self, text):
        if self.text != None:
            raise Exception("Attempting to reset text")
        self.text = text
    

def get_soup(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    return soup

def get_text(soup):
    paras = soup.find_all('p')
    text = []
    for p in paras:
        text.append(p.get_text())

    return "\n".join(text)
    
def scrape_page(url):
    if url not in scrapes:
        soup = get_soup(url)
        text = get_text(soup)
        scrapes[url] = Scrape(soup, text)

    return scrapes[url]