'''
Query Google for news articles

'''
import requests
import json
import pandas as pd

months = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

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



def get_date_of_publication(file_name, error_file_name):
    """
    param: json dump containing search results
    return: dictionary sorted chronology url_link --> date_of_publication
    """
    f = open(file_name, "r")
    results = json.load(f)
    f.close()
    dates = {}
    errors = []
    for item in results['items']:
        try:
            date = item['snippet'].split()[:3]  #mm, dd, yyyy
            dates[item['link']] = (int(date[2]), months[date[0]], int(date[1].replace(',', '')))
        except:
            f = open(error_file_name, 'a')
            f.write(str(item))
            f.close()
            continue

    

    dates = {k: v for k, v in sorted(dates.items(), key=lambda item: item[1])}
    return dates