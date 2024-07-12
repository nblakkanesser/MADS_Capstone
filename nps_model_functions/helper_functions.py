import pandas as pd 
import json
import requests
from openai import OpenAI

from environment import env
config = env.env()

api_base_url = 'https://developer.nps.gov/api/v1/'

def create_prompt_response(row, target):
    """
    Parses the synthetic data into GPT format
    """
    if target == 'endpoint':
        dict = {'prompt': row['query'],
                'completion':f"endpoint: {row['api_call.endpoint']}"}
    elif target == 'parkcode':
        dict = {'prompt': row['query'],
                'completion':f"parkcode: {row['api_call.parkCode']}"}
    elif target == 'intent':
        dict = {'prompt': row['query'],
                'completion':f"{row['intent']}"}
    return dict

def save_to_jsonl(dataframe, filename,target):
    """
    Writes record to json with correct GPT format
    * ChatGPT assisted in writing this function
    """
    with open(filename, 'w') as f:
        for _, row in dataframe.iterrows():
            example = create_prompt_response(row,target)
            json.dump(example, f)
            f.write('\n')
