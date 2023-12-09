'''
Remove irrelevant text - ads/links to other articles
Remove newlines & condense text

'''

from openai import OpenAI


def remove_newlines(text):
    lines = text.split("\n")
    cleaned = " ".join(lines)
    return cleaned

def get_extraneous_text(text):
    client = OpenAI()

    response = client.chat.completions.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        {"role": "user", "content": "Given the following, which sentences are irrelevant to the main point of the article? Use a hyphen and newline to separate the list of sentences." + text}
    ]
    )
    #print(response.choices[0].message.content)
    
    return response.choices[0].message.content

def remove_extraneous_text(text):
    extraneous_text = get_extraneous_text(text)
    extraneous_list = extraneous_text.split("-\n")
    cleaned_text = text
    for item in extraneous_list:
        cleaned_text = cleaned_text.replace(item, '')
    return cleaned_text

def clip(text, threshold=300):
    words = text.split(" ")
    if len(words)>threshold:
        text = " ".join(words[:threshold])
    
    return text

def clean_text(text, date):
    newlines_removed = remove_newlines(text)
    #cleaned_text = remove_extraneous_text(newlines_removed)
    cleaned_text = clip(newlines_removed)
    date_header = "Publication date: "+date+"\n"
    return date_header+cleaned_text