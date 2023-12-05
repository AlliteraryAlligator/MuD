'''
use gpt to summarize multi-doc
'''

from openai import OpenAI
import pandas as pd

def summarize(clean_docs_file, claim_verification_map_file):
    df = pd.read_csv(claim_verification_map_file)
    clean_df = pd.read_csv(clean_docs_file)

    input = ""
    num_tokens = 0
    for d in clean_df['document']:
        num_tokens+=len(d.split(" "))
        input+=d

    summary_num_tokens = int(num_tokens/4)

    print(summary_num_tokens)

    client = OpenAI()

    response = client.chat.completions.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        {"role": "user", "content": "Summarize the following, written in paragraph-style using at least "+str(summary_num_tokens)+" words:" + input}
    ]
    )

    claims = response.choices[0].message.content.split(".")
    rows = [(claim, [], [], [], 0, 0, 0) for claim in claims]

    df2 = pd.DataFrame(rows, columns=['summary_claim', 'contradicts', 'supports', 'dnm', 'contradicts_len', 'supports_len', 'dnm_len'])
    df3 = pd.concat([df, df2])
    df3.to_csv(claim_verification_map_file, header=False, index=False,  mode='a')

    return True