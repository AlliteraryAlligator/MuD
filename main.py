'''
pipeline
'''

from mine import search
from mine import get_date_of_publication
from scrape import scrape_page
from scrape import Scrape
from clean import clean_text
from summarize import summarize
import pandas as pd
import csv

API_KEY = "AIzaSyBqU4K_HDfWYdajj6Kgviu_3hhcfkRU1Ms"
URL = "https://www.googleapis.com/customsearch/v1?key="+API_KEY+"&cx=13d6598f189224dba&q="
RESULTS_PATH = "./results/"
SEARCH_FILE_NAME = "search_results.json"
SCRAPE_FILE_NAME = "raw_scrape.csv"
CLEAN_FILE_NAME = "clean_scrape.csv"
ERROR_FILE_NAME = "errors.txt"
CLAIM_MAP_FILE_NAME = "claim_map.csv"


def get_articles(query):
    url = URL+query
    success = search(url, RESULTS_PATH+SEARCH_FILE_NAME)
    if success:
        return True
    else:
        raise Exception("Error arose while trying to search.")


def scrape_articles():
    links_and_dates = get_date_of_publication(RESULTS_PATH+SEARCH_FILE_NAME, RESULTS_PATH+ERROR_FILE_NAME)
    links = links_and_dates.keys()  #chronologically sorted old->new
    
    scrapes = []
    for link in links:
        scrape = scrape_page(link)
        print(scrape)
        print(Scrape.get_text(scrape))
        scrapes.append((Scrape.get_text(scrape), links_and_dates[link]))

    df = pd.DataFrame(scrapes, columns=['document', 'publication_date'])
    df.to_csv(RESULTS_PATH+SCRAPE_FILE_NAME, index=False)

def clean_articles():
    raw_df = pd.read_csv(RESULTS_PATH+SCRAPE_FILE_NAME)

    cleaned_articles = []

    for i in range(len(raw_df)):
        cleaned = clean_text(raw_df['document'][i])
        cleaned_articles.append((cleaned, raw_df['publication_date'][i]))
    
    clean_df = pd.DataFrame(cleaned_articles, columns=['document', 'publication_date'])
    clean_df.to_csv(RESULTS_PATH+CLEAN_FILE_NAME, index=False)

def summarize_docs():
    df = pd.DataFrame(columns=['summary_claim', 'contradicts', 'supports', 'dnm', 'contradicts_len', 'supports_len', 'dnm_len'])
    df.to_csv(RESULTS_PATH+CLAIM_MAP_FILE_NAME, index=False)

    summarize(RESULTS_PATH+CLEAN_FILE_NAME, RESULTS_PATH+CLAIM_MAP_FILE_NAME)


if __name__=="__main__":
    # all constants
    # writing csv files
    # path related stuff
    # call search/mine
    # read mined data
    # then call scrape on mined data
    query = "venezuelan+elections+news"
    #get_articles(query)
    #scrape_articles()
    #clean_articles()
    summarize_docs()
    print("hello")

    
        