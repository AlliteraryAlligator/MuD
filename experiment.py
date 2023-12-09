from openai import OpenAI
import pandas as pd
import numpy as np
import sklearn
import json
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score


MUD_FILE = "./results/MuD2.json"
EXPERIMENT_RESULTS = "./results/experiment.json"

mud = pd.read_json(MUD_FILE)
prompt = "Using the documents below, answer this true-false question. If there is not enough information, reply with NEI. Do not explain your answer or use punctuation. Your response should either be True, False or NEI.\n"

def run_model(model_name):
    predictions = []
    for i in mud.index:
        print(i)
        question = mud['question'][i]

        documents = mud['documents'][i]
        docs = ""
        for j in range(len(documents)):
            docs+="Document "+str(j)+": "
            key = list(documents[j][1].keys())
            val = documents[j][1][key[0]]
            
            docs+=val+"\n"

        input = prompt+"Q: "+question+"\n"
        input += docs

        client = OpenAI()
        response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": input}
        ]
        )

        reply = response.choices[0].message.content
        gpt_answer = "NEI"

        if "True" in reply:
            gpt_answer = True
        elif "False" in reply:
            gpt_answer = False
        
        predictions.append(gpt_answer)

    return predictions

def run_gpt_turbo():
    predictions = run_model("gpt-3.5-turbo")
    return predictions

def run_gpt_4():
    predictions = run_model("gpt-4")

    return

# from a1
def get_f1(golds, predictions):
    return f1_score(golds, predictions)

def get_e(golds, predictions):
    return accuracy_score(golds, predictions)

def get_recall(golds, predictions):
    return recall_score(golds, predictions)
    
def get_precision(golds, predictions):
    return precision_score(golds, predictions)

def get_type_splits():
    type_counts = mud.value_counts('type')
    sanity_count = type_counts[-1]
    past_counts = type_counts[0]
    anticipation_counts = type_counts[1]

    return (sanity_count, past_counts, anticipation_counts)

def get_stats(golds, predictions):

    f1_score = get_f1(golds, predictions)
    accuracy = get_e(golds, predictions)
    sanity_count, past_counts, anticipation_counts = get_type_splits()
    recall = get_recall(golds, predictions)
    precision = get_precision(golds, predictions)

    return (f1_score, accuracy, sanity_count, past_counts, anticipation_counts, recall, precision)



if __name__=="__main__":
    #run_gpt_turbo()
    #run_gpt_turbo()
    gpt_turbo_results = 0#run_model("gpt-3.5-turbo")
    gpt_4_results = run_model("gpt-4")
    print(gpt_4_results[0:5])
    results = pd.DataFrame(gpt_4_results, columns=['predictions'])
    results.to_json("./results/predictions2.json")

    # results = [gpt_turbo_results, gpt_4_results]

    # #turbo_stats = get_stats(results[0][0], results[0][1])
    # gpt_4_stats = get_stats(results[1][0], results[1][1])

    # # turbo_stats.append(results[0][0])
    # # turbo_stats.append(results[0][1])

    # gpt_4_stats.append(results[1][0])
    # gpt_4_stats.append(results[1][1])

    # stats = pd.DataFrame([gpt_4_stats], columns=['f1_score', 'accuracy', 'sanity_count', 'past_count', 'anticipation_count', 'recall', 'precision', 'labels', 'predictions'])
    # stats.to_json(EXPERIMENT_RESULTS)
