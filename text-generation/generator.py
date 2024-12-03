import pandas as pd

from WikiSpark_API import WikiSpark_API_key
from openai import OpenAI

client = OpenAI(
    organization="org-gCNsUWlm38tlmiYgLBmlohiN",
    project="proj_yOJuKHUY1TB3ex0EfEmrMPCz",
    api_key=WikiSpark_API_key
)

dataframe_path = r'C:\Users\danie\PycharmProjects\WikiSpark\analyzer\tanc2_pubmed_abstracts_2024-11-26_19.37.csv'
df = pd.read_csv(dataframe_path)


completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are a scientist that wants to write a paper about a topic unknown to mankind."
                }
            ]
        },
        {
            "role": "user",
            "content": "Who was Antonio Vivaldi? Answer in 5 lines and in Venetian dialect"
        }
    ]
)

print(completion.choices[0].message.content)
# print(completion.choices[0].message)
