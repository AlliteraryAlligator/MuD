'''
use gpt to summarize multi-doc
'''

from openai import OpenAI
import pandas as pd

SUMMARY_SPLIT = .25

def summarize(clean_docs_file, q_id):
    clean_df = pd.read_json(clean_docs_file)
    #only want the docs that match with 'q_id'

    input = ""

    for doc in clean_df.loc[clean_df['query_id']==q_id]['document']:
        input+=doc
    
    num_tokens = len(input.split(" "))
    summary_num_tokens = int(SUMMARY_SPLIT*num_tokens)
    print(num_tokens)
    client = OpenAI()

    response = client.chat.completions.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        {"role": "user", "content": "Summarize the following using at least "+str(summary_num_tokens)+" words in bullet-point style. The bullets should be hyphens:" + input}
    ]
    )

    summary = response.choices[0].message.content
    #print(summary)

    claims = [claim.strip() for claim in summary.split("-")]
    claims = [claim for claim in claims if claim!=""]
    #print(claims)

    return claims

def gather_excerpts(clean_docs_file, claim, query_id):
    clean_df = pd.read_json(clean_docs_file)

    c_unique = 0
    s_unique = 0
    contradictions = []
    support = []

    for j in clean_df.loc[clean_df['query_id']==query_id].index:
        doc = clean_df['document'][j]
        doc_id = clean_df['doc_id'][j]
        date = clean_df['publication_date'][j]

        contradict_query = "Consider this claim: "+claim+"\nCollect and list excerpts from the following document that contradict with the claim, if any, separated by a hyphen and newline If none, reply None.:\n" + doc
        support_query = "Consider this claim: "+claim+"\nCollect and list excerpts from the following document that support the claim, if any, separated by a hyphen and newline. If none, reply None.:\n" + doc

        #CONTRADICTING EXCERPTS
        client = OpenAI()
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": contradict_query}
        ]
        )

        reply = response.choices[0].message.content
        c_excerpts = []
        if not reply.startswith("None."):
            c_excerpts = reply.split("-\n")

        for excerpt in c_excerpts:
            contradictions.append((doc_id, excerpt))

        #SUPPORTING EXCERPTS
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": support_query}
        ]
        )

        reply = response.choices[0].message.content
        s_excerpts = []
        if not reply.startswith("None."):
            s_excerpts = reply.split("-\n")

        for excerpt in s_excerpts:
            support.append((doc_id, excerpt))
        #support.append((doc_id, excerpt) for excerpt in s_excerpts)

       

        #COUNT UNIUQE
        if len(c_excerpts) > 0:
            c_unique+=1

        if len(s_excerpts) > 0:
            s_unique+=1



    return (contradictions, support, c_unique, s_unique)

    #returns ([contradicting excerpts], [supporting excerpts], c_unique_count, s_unique_count) --> [(doc_id, date, excerpt)]


def find_conflicts(claim_map_file, q_id, claim_id):
    # what is the conflict between the contradiction-supporting excerpts

    claim_df = pd.read_json(claim_map_file)


    contradicting_excerpts = claim_df.loc[(claim_df['claim_id']==claim_id) & (claim_df['query_id']==q_id)]['contradicts']
    supporting_excerpts = claim_df.loc[(claim_df['claim_id']==claim_id) & (claim_df['query_id']==q_id)]['supports']

    excerpts = contradicting_excerpts + supporting_excerpts

    input = "Given the following sentences, what is the point they differ on? Answer in one sentence.\n"
    #print(input)
    num_sentences = 0
    for excerpt in excerpts:
        #print(excerpt)
        for e in excerpt:
            #print("excerpt",e[1])
            if e[1] != "None.":
                input+=e[1]+"\n"
                num_sentences+=1

    if num_sentences==0:
        return None
    
    
    try:
        client = OpenAI()
        response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "user", "content": input}
        ]
        )

        conflict = response.choices[0].message.content
        return conflict
    except:
        return None

def convert_to_question(sentence):
    if sentence!=None and not sentence.startswith("None."):
        input = "The following sentence describes a conflict between documents. Phrase the conflict as a question. There should be no mention of documents. On a newline, rewrite the same question into the future conditional tense.: "+sentence
        #print(sentence)
        client = OpenAI()
        response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": input}
        ]
        )

        open_questions = response.choices[0].message.content.split("\n")
        if len(open_questions)!=2:
            return [None, None]
        #print(open_questions)
        return open_questions   #[past, future]

    return [None, None]




### commented-out code:
# def summarize(clean_docs_file, claim_verification_map_file):
#     df = pd.read_json(claim_verification_map_file)
#     clean_df = pd.read_json(clean_docs_file)

#     input = ""
#     num_tokens = 0
#     for d in clean_df['document']:
#         num_tokens+=len(d.split(" "))
#         input+=d

#     summary_num_tokens = int(num_tokens/4)

#     print(summary_num_tokens)

#     client = OpenAI()

#     response = client.chat.completions.create(
#     model="gpt-3.5-turbo-16k",
#     messages=[
#         {"role": "user", "content": "Summarize the following, written in paragraph-style using at least "+str(summary_num_tokens)+" words:" + input}
#     ]
#     )

#     claims = response.choices[0].message.content.split(".")
#     rows = [(claim, [], [], [], 0, 0, 0) for claim in claims]

#     df2 = pd.DataFrame(rows, columns=['summary_claim', 'contradicts', 'supports', 'dnm', 'contradicts_len', 'supports_len', 'dnm_len'])
#     df3 = pd.concat([df, df2])
#     df3.to_csv(claim_verification_map_file, header=False, index=False,  mode='a')

#     return True