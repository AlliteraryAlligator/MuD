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
    model="gpt-4",
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

def clean_text(text):
    newlines_removed = remove_newlines(text)
    cleaned_text = remove_extraneous_text(newlines_removed)
    return cleaned_text