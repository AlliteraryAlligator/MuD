'''
Query Google for news articles

'''
import requests
import json
import pandas as pd

def search(url, file_name):
    r = requests.get(url = url)
    results = r.json()
    with open(file_name, 'w') as fp:
        json.dump(results, fp)
    return True


def get_titles(file_name):
    """
    param: json dump containing search results
    return: list of article titles
    """
    f = open(file_name, "r")
    results = json.load(f)
    f.close()
    titles = []
    for item in results['items']:
        titles.append(item['title'])
    
    return titles


def get_links(file_name):
    """
    param: json dump containing search results
    return: list of article links/urls
    """
    f = open(file_name, "r")
    results = json.load(f)
    f.close()
    links = []
    for item in results['items']:
        links.append(item['link'])
    
    return links



def get_date_of_publication(file_name):
    """
    param: json dump containing search results
    return: dictionary sorted chronology url_link --> date_of_publication
    """
    f = open(file_name, "r")
    results = json.load(f)
    f.close()
    dates = {}
    for item in results['items']:
        try:
            dates[item['link']] = item['pagemap']['metatags'][0]['article:published_time']
        except:
            continue
    
    dates = {k: v for k, v in sorted(dates.items(), key=lambda item: item[1])}
    return dates