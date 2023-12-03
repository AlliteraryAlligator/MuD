'''
pipeline
'''

from mine import search
from mine import get_date_of_publication
from scrape import scrape_page
from scrape import Scrape
import pandas as pd
import csv

API_KEY = "AIzaSyBqU4K_HDfWYdajj6Kgviu_3hhcfkRU1Ms"
URL = "https://www.googleapis.com/customsearch/v1?key="+API_KEY+"&cx=13d6598f189224dba&q="
RESULTS_PATH = "./results/"
SEARCH_FILE_NAME = "search_results.json"
SCRAPE_FILE_NAME = "raw_scrape.csv"


def get_articles(query):
    url = URL+query
    success = search(url, RESULTS_PATH+SEARCH_FILE_NAME)
    if success:
        return True
    else:
        raise Exception("Error arose while trying to search.")


def scrape_articles():
    links_and_dates = get_date_of_publication(RESULTS_PATH+SEARCH_FILE_NAME)
    links = links_and_dates.keys()  #chronologically sorted old->new
    
    scrapes = []
    for link in links:
        scrape = scrape_page(link)
        print(scrape)
        print(Scrape.get_text(scrape))
        scrapes.append((Scrape.get_text(scrape), links_and_dates[link]))

    df = pd.DataFrame(scrapes, columns=['document', 'publication_date'])
    df.to_csv(RESULTS_PATH+SCRAPE_FILE_NAME, index=False)

if __name__=="__main__":
    # all constants
    # writing csv files
    # path related stuff
    # call search/mine
    # read mined data
    # then call scrape on mined data
    query = "venezuelan+elections+news"
    #get_articles(query)
    scrape_articles()
    print("hello")

    
        