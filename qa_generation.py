'''
use gpt to compare claims in summary to individual documents
CONTRADICTS, SUPPORTS, DNM
'''

from openai import OpenAI
import pandas as pd



def generate_answers():

    return

def generate_temporal_QA(consensus_file, temporal_split_file, doc_to_consensus_file, q_id, scrape_file):
    # By ___ the general consensus was that ___
    consensus_df = pd.read_json(consensus_file)
    doc_consensus_df = pd.read_json(doc_to_consensus_file)
    temporal_df = pd.read_json(temporal_split_file)

    questions = []
    answers = []
    for j in temporal_df.index:
        if temporal_df['query_id'][j]!=q_id:
            continue
        date_split = temporal_df['date'][j]
        display_date = str(date_split[1])+"/"+str(date_split[2])+"/"+str(date_split[0])
        temporally_valid_docs = temporal_df['doc_ids'][j]
        temporally_valid_docs = list(temporally_valid_docs.values())
        num_voters = len(temporally_valid_docs)
        #print(num_voters)
        #print(temporally_valid_docs)
        valid_consensuses = []

        for k in doc_consensus_df.loc[doc_consensus_df['query_id']==q_id].index:
            d = doc_consensus_df['doc_id'][k]
            
            doc_id = d
            #print(doc_id)
            if doc_id in temporally_valid_docs:
                consensus_id = doc_consensus_df['consensus_id'][k]
                valid_consensuses.append(consensus_id)

        
        for i in consensus_df.loc[consensus_df['query_id']==q_id].index:
            consensus = consensus_df['consensus'][i]
            c_id = consensus_df['consensus_id'][i]

            type_anticipation = consensus_df['type'][i]
            if consensus==None:
                continue
            try:
                question = "Imagine today is "+display_date+". The general consensus currently is that "+consensus
                questions.append((question, type_anticipation))
            except:
                try:
                    question = "Imagine today is "+display_date+". The general consensus currently is that "+list(consensus.values())[0]
                    questions.append((question, type_anticipation))
                except:
                    continue

            num_votes = valid_consensuses.count(c_id)
            
            #print(num_votes)
            verdict = "NEI"
            if num_votes > int(num_voters/2):
                print("yes")
                verdict = True
            elif num_votes < num_voters/2:
                verdict = False

            answers.append(verdict)


    # for i in temporal_df.index:
    #     query_id = temporal_df['query_id'][i]
        
    #     if query_id!=q_id:
    #         continue

    #     date_split = temporal_df['date'][i]
    #     docs = temporal_df['doc_ids'][i]

    #     display_date = str(date_split[1])+"/"+str(date_split[2])+"/"+str(date_split[0])
    #     #print(display_date)
    #     #find winner consensus id
    #     #query_id, docs --> grab all consensus_ids
    #     #find one singular mode if it exists, else No Consensus
    #     consensus_winner = -1
    #     doc_consensuses = []
    #     #d = doc_consensus_df.loc[doc_consensus_df['query_id']==query_id]
        
    #     for val in list(docs.values()):
    #         print(doc_consensus_df['doc_id'][1])
    #         chosen = doc_consensus_df.loc[(doc_consensus_df['query_id']==query_id) & (doc_consensus_df['doc_id'].values()==val)]['consensus_id']
    #         print("chosen:", chosen)
    #         for c in chosen:
    #             doc_consensuses.append(c)
    #     # for c in d.query('doc_id in '+str(list(docs.values())))['consensus_id']:
    #     #     doc_consensuses.append(c)
    #     return
    #     freqs = [doc_consensuses.count(dc) for dc in set(doc_consensuses)]
    #     freqs.sort()
    #     print("freq:", len(freqs))
    #     if len(freqs) == 0:
    #         consensus_winner = 1
    #     elif freqs.count(freqs[-1]) == 1:
    #         consensus_winner = freqs[-1]
    #         #otherwise there was a tie at the top level and so there's No Consensus

    #     for j in consensus_df.loc[consensus_df['query_id']==query_id].index:
    #         consensus = consensus_df['consensus'][j]
    #         consensus_id = consensus_df['consensus_id'][j]
    #         type_anticipation = consensus_df['type'][j]
    #         try:
    #             question = "Imagine today is "+display_date+". The general consensus currently is that "+consensus
    #             questions.append((question, type_anticipation))
    #         except:
    #             continue
            
    #         if consensus_winner==-1:
    #             answers.append("NEI")
    #         else:
    #             answers.append(consensus_winner==consensus_id)
            
    return (questions, answers)

def generate_sanity_QA(claim_map_file, query_id):
    # not temporal
    claim_df = pd.read_json(claim_map_file)

    sanity_questions = []

    for i in claim_df.loc[(claim_df['query_id']==query_id) &(claim_df["type"]==-1)].index:
        claim = claim_df['claim']
        question = "The general consensus is that "+claim
        sanity_questions.append(question)

    sanity_answers = [True]*len(sanity_questions)

    return (sanity_questions, sanity_answers) #answers should all be TRUE


def collect_consensuses(claim_map_file, q_id, claim_id, open_q_id):
    claim_df = pd.read_json(claim_map_file)

    contradicting_excerpts = claim_df.loc[(claim_df['claim_id']==claim_id) & (claim_df['query_id']==q_id) & (claim_df['open_question_id']==open_q_id)]['contradicts']
    supporting_excerpts = claim_df.loc[(claim_df['claim_id']==claim_id) & (claim_df['query_id']==q_id) & (claim_df['open_question_id']==open_q_id)]['supports']
    open_ended_question = claim_df.loc[(claim_df['claim_id']==claim_id) & (claim_df['query_id']==q_id) & (claim_df['open_question_id']==open_q_id)]['open_question']
    
    
    try:
        open_ended_question = open_ended_question
        #print(open_ended_question)
    except:
        return []
    excerpts = contradicting_excerpts + supporting_excerpts
    answers = []
    
    for excerpt in excerpts:
        for e in excerpt:
            open_ended_answer = None
            
            if e[1] != "None." and open_ended_question.item() != "None." and open_ended_question.item() != None:
                
                input = "Given the document below, answer this question: "+open_ended_question.item()+"\n"
                input += "Document: "+e[1]

                client = OpenAI()
                response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": input}
                ]
                )

                open_ended_answer = response.choices[0].message.content
            
            answers.append((e[0], open_ended_question.item(), open_ended_answer, e[1]))     #doc id, question, answer, excerpt
        
    # #answers for a particular group of excerpts relevant to a particular claim

    return answers


def consolidate_consensuses(answer_map_file, query_id, open_q_id, open_question):
    answer_map_df = pd.read_json(answer_map_file)
    open_ended_answers = answer_map_df.loc[(answer_map_df['query_id']==query_id) & (answer_map_df['open_q_id']==open_q_id)]['open_answer']
    open_answer_id = answer_map_df.loc[(answer_map_df['query_id']==query_id) & (answer_map_df['open_q_id']==open_q_id)]['open_answer_id']
    
    if open_question!=None:
        input = "The following is a question and a list of phrases that are responses to the question, answered by different sources. Bucket the phrases so that each bucket has the same answer to the question. For each group, only list out the phrase-ids. Buckets should be newline separated, and on each line, phrase-ids in the bucket should be comma-separated.\n"
        input += "Question: "+open_question+"\n"
        input += "Phrases:\n"
        
        
        for i in open_ended_answers.index:
            
            try:
                if open_answer_id[i] == None:
                    continue
                input += str(open_answer_id[i])+", "+open_ended_answers[i]+"\n"
                
            except:
                continue
        
        client = OpenAI()
        response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": input}
        ]
        )
        reply = response.choices[0].message.content
        
        buckets = [bucket.split(",") for bucket in reply.split("\n")]
        
        consensuses = []    #(consensus, [open_answer_ids], [doc_ids])
        for bucket in buckets:
            if len(bucket) > 1:
                input = "Summarize all of the following: \n"
                ids = []
                doc_ids = set()
                for phrase in bucket:
                    
                    try:
                        id = int(phrase.strip())
                        
                        phrase = answer_map_df.loc[(answer_map_df['query_id']==query_id) & (answer_map_df['open_answer_id']==id)]['open_answer']
                        doc_id = answer_map_df.loc[(answer_map_df['query_id']==query_id) & (answer_map_df['open_answer_id']==id)]['doc_id']
                        input+=str(phrase)+"\n"
                        ids.append(id)
                        doc_ids.add(doc_id)
                        
                    except:
                        continue

                client = OpenAI()
                response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": input}
                ]
                )
                
                bucket_summary = response.choices[0].message.content
                consensuses.append((bucket_summary, ids, list(doc_ids)))
            else:
                try:
                    id = int(bucket[0])
                    phrase = answer_map_df.loc[(answer_map_df['query_id']==query_id) & (answer_map_df['open_answer_id']==id)]['open_answer']
                    doc_id = answer_map_df.loc[(answer_map_df['query_id']==query_id) & (answer_map_df['open_answer_id']==id)]['doc_id']
                    consensuses.append((phrase, [id], [doc_id]))
                except:
                    continue

        return consensuses
    
    return []










##### commented out code
# """
# for each summary claim, compare it with a document, grab excerpts that agree and disagree
# put statements (date, doc_id, statement) into the respective bucket in the df
# look at summary claims that have contradictions>0 and relevant_unique>1
#     relevant_unique = count of unique documents that contribute to the cause
#     contradictions_count = number of contradicting excerpts (could be from the same document)

# """

# def get_excerpts(claim_map_file, clean_doc_file):
#     claim_df = pd.read_csv(claim_map_file)
#     clean_df = pd.read_csv(clean_doc_file)
    
#     rows = []

#     for i in claim_df.index:
#         claim = claim_df['summary_claim'][i]
#         c_unique = 0
#         s_unique = 0

#         contradictions = []
#         support = []

#         for j in clean_df.index:
#             doc = clean_df['document'][j]
#             doc_id = clean_df['document_id'][j]
#             date_id = clean_df['publication_date'][j]
            

#             contradict_query = "Consider this claim: "+claim+"\nCollect and list excerpts from the following document that contradict with the claim, if any, separated by a hyphen and newline:\n" + doc
#             support_query = "Consider this claim: "+claim+"\nCollect and list excerpts from the following document that support the claim, if any, separated by a hyphen and newline:\n" + doc


#             client = OpenAI()
#             response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "user", "content": contradict_query}
#             ]
#             )

#             contradictions.append((doc_id, date_id, response.choices[0].message.content.split("-\n")))

#             response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "user", "content": support_query}
#             ]
#             )

#             support.append((doc_id, date_id, response.choices[0].message.content.split("-\n")))

#             if len(contradictions) > 0:
#                 c_unique+=1

#             if len(support) > 0:
#                 s_unique+=1

        
#         rows.append((contradictions, support, c_unique, s_unique))


#     new_claim_df = pd.DataFrame(rows, columns=['contradicts', 'supports', 'contradicts_len', 'supports_len'])
#     claim_df.update(new_claim_df)
    
#     claim_df.to_csv(claim_map_file, index=False)




            






