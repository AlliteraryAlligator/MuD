'''
pipeline
'''

from mine import search
from mine import get_date_of_publication
from scrape import scrape_page
from scrape import Scrape
from clean import clean_text
from claim_decomposition import summarize
from claim_decomposition import gather_excerpts
from claim_decomposition import find_conflicts
from claim_decomposition import convert_to_question
from qa_generation import collect_consensuses
from qa_generation import consolidate_consensuses
from qa_generation import generate_sanity_QA
from qa_generation import generate_temporal_QA
#from verify import get_excerpts
import pandas as pd
import csv
import random
import json

API_KEY = "AIzaSyBqU4K_HDfWYdajj6Kgviu_3hhcfkRU1Ms"
URL = "https://www.googleapis.com/customsearch/v1?key="+API_KEY+"&cx=13d6598f189224dba&tmb=nws&q="
RESULTS_PATH = "./results/"
QUERY_FILE_NAME = "queries.json"
TEMPORAL_SPLIT_FILE_NAME = "temporal.json"
SEARCH_FILE_NAME = "search_results.json"
SCRAPE_FILE_NAME = "raw_scrape.json"
CLEAN_FILE_NAME = "clean_scrape.json"
SUMMARY_FILE_NAME = "summaries.json"
CLAIM_MAP_FILE_NAME = "claim_map.json"
OPEN_ANSWER_FILE_NAME = "open_answers.json"
CONSENSUS_FILE_NAME = "consensus.json"
DOC_CONSENSUS_MAP_FILE_NAME  = "doc_to_consensus.json"
QA_FILE_NAME = "MuD2.json"
ERROR_FILE_NAME = "errors.txt"

# id-ranges
ID_START_RANGE = 10000
ID_END_RANGE = 90000


def get_queries():
    queries = ["venezuelan+elections+news", 
               "Jan+6th+insurrection+news+articles+written+in+jan+2021", 
               "venezuelan+elections+news+from+october", 
               "Jan+6th+criminal+proceedings+news+articles",
               "Ukraine+War+news+articles+written+in+2022",
               "Israel+Gaza+news+articles+from+october+2023"]
    query_ids = []

    for query in queries:
        query_ids.append((random.randint(ID_START_RANGE, ID_END_RANGE), query))

    df = pd.DataFrame(query_ids, columns=['query_id', 'query'])
    df.to_json(RESULTS_PATH+QUERY_FILE_NAME)

def get_articles():
    query_df = pd.read_json(RESULTS_PATH+QUERY_FILE_NAME)
    search_results = []
    scrapes = []
    for i in query_df.index:
        url = URL+query_df['query'][i]
        
        query_results = search(url)
        search_results.append((query_df['query_id'][i], query_results))

        links_and_dates = get_date_of_publication(query_results, RESULTS_PATH+ERROR_FILE_NAME)
        links = links_and_dates[0].keys()  #chronologically sorted old->new
        
        for link in links:
            scrape = scrape_page(link)
            scrapes.append((query_df['query_id'][i], random.randint(ID_START_RANGE, ID_END_RANGE), Scrape.get_text(scrape), links_and_dates[0][link], links_and_dates[1]))

    results_df = pd.DataFrame(search_results, columns=['query_id', 'results'])
    results_df.to_csv(RESULTS_PATH+SEARCH_FILE_NAME, index=False)

    scrapes_df = pd.DataFrame(scrapes, columns=['query_id', 'doc_id', 'document', 'publication_date', 'display_date'])
    scrapes_df.to_json(RESULTS_PATH+SCRAPE_FILE_NAME)

def clean_articles():
    raw_df = pd.read_json(RESULTS_PATH+SCRAPE_FILE_NAME)

    cleaned_articles = []

    for i in raw_df.index:
        display_date = raw_df['display_date'][i]
        
        cleaned = clean_text(raw_df['document'][i], display_date)
        cleaned_articles.append((raw_df['query_id'][i], raw_df['doc_id'][i], cleaned, raw_df['publication_date'][i]))
    
    clean_df = pd.DataFrame(cleaned_articles, columns=['query_id', 'doc_id', 'document', 'publication_date'])
    clean_df.to_json(RESULTS_PATH+CLEAN_FILE_NAME)

def get_temporal_splits():
    
    raw_df = pd.read_json(RESULTS_PATH+SCRAPE_FILE_NAME)

    rows = []
    for query_id in raw_df['query_id'].unique():
        #dates = set(dates)
        dates = sorted(raw_df.loc[raw_df['query_id']==query_id]['publication_date'])

        if len(dates) >= 3:
        
            split_len_1 = int(len(dates)/3)
            split_len_2 = int((len(dates) - split_len_1)/2)

            start1 = dates[split_len_1-1]
            start2 = dates[split_len_1+split_len_2-1]
            print(type(start1))

            result_df = raw_df.loc[
                (raw_df['query_id'] == query_id) & 
                (raw_df['publication_date'].apply(lambda x: tuple(x) >= tuple(start1))),
                :
            ]['doc_id']

            rows.append((query_id, start1, result_df))

            result_df2 = raw_df.loc[
                (raw_df['query_id'] == query_id) & 
                (raw_df['publication_date'].apply(lambda x: tuple(x) >= tuple(start2))),
                :
            ]['doc_id']
            
            rows.append((query_id, start2, result_df2))

        rows.append((query_id, dates[-1], raw_df.loc[raw_df['query_id']==query_id]['doc_id']))

    temporal_df = pd.DataFrame(rows, columns=['query_id', 'date', 'doc_ids'])
    temporal_df.to_json(RESULTS_PATH+TEMPORAL_SPLIT_FILE_NAME)

    return

def summarize_docs():
    clean_df = pd.read_json(RESULTS_PATH+CLEAN_FILE_NAME)

    claims = []

    for query in clean_df['query_id'].unique():

        #query_id, claim_id, claim
        sentences = summarize(RESULTS_PATH+CLEAN_FILE_NAME, query)
        for sentence in sentences:
            claims.append((query, random.randint(ID_START_RANGE, ID_END_RANGE), sentence))
        
    summaries_df = pd.DataFrame(claims, columns=['query_id', 'claim_id', 'claim'])
    summaries_df.to_json(RESULTS_PATH+SUMMARY_FILE_NAME)

def contradict_support_claim():
    summary_df = pd.read_json(RESULTS_PATH+SUMMARY_FILE_NAME)

    rows = []

    for i in summary_df.index:
        query_id = summary_df['query_id'][i]
        claim_id = summary_df['claim_id'][i]
        claim = summary_df['claim'][i]
        if claim != "":
            print(claim)

            excerpts = gather_excerpts(RESULTS_PATH+CLEAN_FILE_NAME, claim, query_id) #([doc_id, date, excerpt], [doc_id, date_excerpt], #c_unique, #s_unique)
            
            sanity = 0
            if len(excerpts[0])==0:
                sanity = -1

            rows.append((query_id, claim_id, claim, excerpts[0], excerpts[1], excerpts[2], excerpts[3], sanity, None, None, None))
            rows.append((query_id, claim_id, claim, excerpts[0], excerpts[1], excerpts[2], excerpts[3], sanity, None, None, None))
            

    claim_df = pd.DataFrame(rows, columns=['query_id', 'claim_id', 'claim', 'contradicts', 'supports', 'contradicts_len', 'supports_len', 'type', 'issue', 'open_question_id', 'open_question'])
    claim_df.to_json(RESULTS_PATH+CLAIM_MAP_FILE_NAME)

def get_conflicts():
    claim_df = pd.read_json(RESULTS_PATH+CLAIM_MAP_FILE_NAME)

    claim_map_p2 = []

    for i in claim_df.index:
        
        if claim_df['type'][i]<0:
            continue

        query_id = claim_df['query_id'][i]
        claim_id = claim_df['claim_id'][i]
        
        conflict = find_conflicts(RESULTS_PATH+CLAIM_MAP_FILE_NAME, query_id, claim_id)
        
        open_questions = convert_to_question(conflict)
        print(open_questions[0])
        claim_map_p2.append((conflict, random.randint(ID_START_RANGE, ID_END_RANGE), open_questions[0], 0))
        claim_map_p2.append((conflict, random.randint(ID_START_RANGE, ID_END_RANGE), open_questions[1], 1))
        

    claim_df2 = pd.DataFrame(claim_map_p2, columns=['issue', 'open_question_id', 'open_question', 'type'])
    claim_df.update(claim_df2)
    claim_df.to_json(RESULTS_PATH+CLAIM_MAP_FILE_NAME)

    return


def collect_open_answers():
    claim_df = pd.read_json(RESULTS_PATH+CLAIM_MAP_FILE_NAME)
    rows = []

    for i in claim_df.index:
        query_id = claim_df['query_id'][i]
        claim_id = claim_df['claim_id'][i]
        open_q_id = claim_df['open_question_id'][i]
        type_anticipation = 0

        answers = collect_consensuses(RESULTS_PATH+CLAIM_MAP_FILE_NAME, query_id, claim_id, open_q_id)
        
        for answer in answers:
            rows.append((query_id, open_q_id, answer[1], answer[0], answer[3], random.randint(ID_START_RANGE, ID_END_RANGE), answer[2], type_anticipation))
        
    
    open_answers_df = pd.DataFrame(rows, columns=['query_id', 'open_q_id', 'open_q', 'doc_id', 'excerpt', 'open_answer_id', 'open_answer', 'type'])
    open_answers_df.to_json(RESULTS_PATH+OPEN_ANSWER_FILE_NAME)

def reach_consensus():
    answer_df = pd.read_json(RESULTS_PATH+OPEN_ANSWER_FILE_NAME)

    consensus = []
    doc_to_consensus = []
    for i in answer_df.index:
        
        print(i)
        query_id = answer_df['query_id'][i]
        open_q_id = answer_df['open_q_id'][i]
        open_q = answer_df['open_q'][i]
        type_anticipation = answer_df['type'][i]

        #(consensus, [open_answer_ids], [doc_ids])
        consensuses = consolidate_consensuses(RESULTS_PATH+OPEN_ANSWER_FILE_NAME, query_id, open_q_id, open_q)
        
        for c in consensuses:
            consensus_id = random.randint(ID_START_RANGE, ID_END_RANGE)
            consensus.append((query_id, open_q_id, open_q, consensus_id, c[0], c[2], type_anticipation))
            
            for id in c[2]:
                try:
                    doc_to_consensus.append((query_id, open_q_id, id.item(), consensus_id, type_anticipation))
                except:
                    continue
                
    consensus_df = pd.DataFrame(consensus, columns=['query_id', 'open_q_id', 'open_q', 'consensus_id', 'consensus', 'doc_ids', 'type'])
    consensus_df.to_json(RESULTS_PATH+CONSENSUS_FILE_NAME)

    doc_consensus_df = pd.DataFrame(doc_to_consensus, columns=['query_id', 'open_q_id', 'doc_id', 'consensus_id', 'type'])
    doc_consensus_df.to_json(RESULTS_PATH+DOC_CONSENSUS_MAP_FILE_NAME)
    
    return

def get_questions():

    clean_df = pd.read_json(RESULTS_PATH+CLEAN_FILE_NAME)
    #sanity_df = pd.read_json(RESULTS_PATH+QA_FILE_NAME)
    rows = []

    for query_id in clean_df['query_id'].unique():
        print(query_id)
        questions, answers = generate_temporal_QA(RESULTS_PATH+CONSENSUS_FILE_NAME, RESULTS_PATH+TEMPORAL_SPLIT_FILE_NAME, RESULTS_PATH+DOC_CONSENSUS_MAP_FILE_NAME, query_id, RESULTS_PATH+SCRAPE_FILE_NAME)
        
        docs = []

        for id in clean_df.loc[clean_df['query_id']==query_id]['doc_id']:
            doc = clean_df.loc[(clean_df['query_id']==query_id) & (clean_df['doc_id']==id)]['document']
            #date = clean_df.loc[(clean_df['query_id']==query_id) & (clean_df['doc_id']==id)]['publication_date']
            docs.append((id, doc))

        for j in range(len(questions)):
            rows.append((query_id, random.randint(ID_START_RANGE, ID_END_RANGE), questions[j][0], docs, answers[j], questions[j][1]))
    
    qa_df = pd.DataFrame(rows, columns=['query_id', 'question_id', 'question', 'documents', 'answer', 'type'])
    #mud = pd.concat([sanity_df, qa_df])
    #mud.to_json(RESULTS_PATH+QA_FILE_NAME)
    qa_df.to_json(RESULTS_PATH+QA_FILE_NAME)
    return

def get_sanity_questions():
    clean_df = pd.read_json(RESULTS_PATH+CLEAN_FILE_NAME)
    rows = []

    for query_id in clean_df['query_id'].unique():
    
        questions, answers = generate_sanity_QA(RESULTS_PATH+CLAIM_MAP_FILE_NAME, query_id)

        docs = []

        for id in clean_df.loc[clean_df['query_id']==query_id]['doc_id']:
            doc = clean_df.loc[(clean_df['query_id']==query_id) & (clean_df['doc_id']==id)]['document']
            #date = clean_df.loc[(clean_df['query_id']==query_id) & (clean_df['doc_id']==id)]['publication_date']
            docs.append((id, doc))
        
        for j in range(len(questions)):
            rows.append((query_id, random.randint(ID_START_RANGE, ID_END_RANGE), questions[j], docs, answers[j], '-1'))
        
    sanity_df = pd.DataFrame(rows, columns=['query_id', 'question_id', 'question', 'documents', 'answer', 'type'])
    sanity_df.to_json(RESULTS_PATH+QA_FILE_NAME)

if __name__=="__main__":
    # all constants
    # writing json files
    # path related stuff
    # call search/mine
    # read mined data
    # then call scrape on mined data
    
    # get_queries()
    print("got queries")
    # get_articles()
    print("got articles")
    print("scraped articles")
    # clean_articles()
    print("cleaned articles")
    # get_temporal_splits()
    print("got temporal splits")
    # summarize_docs()
    print("summarized docs")
    # contradict_support_claim()
    print("contradict support stuff done")
    # get_conflicts()
    print("got conflicts")
    # collect_open_answers()
    print("collected open answers")
    # reach_consensus()
    print("reached answers")
    #get_sanity_questions()
    print("got sanity questions")
    get_questions()
    print("got real questions")
    # print("created mud dataset!")


    
        

### commented out code ###



# find conflicts

# def summarize_docs():
#     df = pd.DataFrame(columns=['summary_claim', 'contradicts', 'supports', 'dnm', 'contradicts_len', 'supports_len', 'dnm_len'])
#     df.to_csv(RESULTS_PATH+CLAIM_MAP_FILE_NAME, index=False)

#     summarize(RESULTS_PATH+CLEAN_FILE_NAME, RESULTS_PATH+CLAIM_MAP_FILE_NAME)



# def scrape_articles():
#     results_df = pd.read_csv(RESULTS_PATH+SEARCH_FILE_NAME)

#     for i in results_df.index:
#         json_dump = results_df['results'][i]
        
#         links_and_dates = get_date_of_publication(json_dump, RESULTS_PATH+ERROR_FILE_NAME)
#         links = links_and_dates[0].keys()  #chronologically sorted old->new
        
#         scrapes = []
#         for link in links:
#             scrape = scrape_page(link)
#             scrapes.append((results_df['query_id'][i], random.randint(ID_START_RANGE, ID_END_RANGE), Scrape.get_text(scrape), links_and_dates[0][link], links_and_dates[1]))

#     scrapes_df = pd.DataFrame(scrapes, columns=['query_id', 'doc_id', 'document', 'publication_date', 'display_date'])
#     scrapes_df.to_csv(RESULTS_PATH+SCRAPE_FILE_NAME, index=False)