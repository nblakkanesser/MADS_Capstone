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
    if target == 'parkcode':
        dict = {'prompt': row['query'],
                'completion':f"parkcode: {row['api_call.parkCode']}"}
    return dict

def save_to_jsonl(dataframe, filename,target):
    """
    Writes record to json with correct GPT format
    * ChatGPT was used to assist in writing this function
    """
    with open(filename, 'w') as f:
        for _, row in dataframe.iterrows():
            example = create_prompt_response(row,target)
            json.dump(example, f)
            f.write('\n')

def handle_query(query, model, client, max_tokens):
    """
    Uses a fine tuned model to interpret query into necessary API results based on the model parameter. 

    query (str): A user defined query.
    model (str): The job id of the fine tuned GPT model. Can be found on the GPT fine tuning dashboard under 'Job ID' on the associated model.
    client (obj): Authorization through API key to GPT console.
    max_tokens (int): Number of tokens to limit response to. (Parameter is a misnomer as the response will try to fit 50 tokens if max is set to 50)
    * Function was created using OpenAI fine-tuning documentation
    """
    prompt = f"prompt: {query}\n"
    response = client.completions.create(
        model=model,  
        prompt=prompt,
        max_tokens=max_tokens
    )
    completion = response.choices[0].text
    return completion

def get_params(query):
    """
    Function to use finetuned model to find endpoint and parkcode for an API call on a specific query.

    query (str): A user defined query.
    """
    # Define input variables
    client = OpenAI(api_key  = config['gpt_api_key'])
    gpt_parkcode_model = config['gpt_parkcode_model']
    gpt_endpoint_model = config['gpt_endpoint_model']

    # Load models from OpenAI
    parkcode_model = client.fine_tuning.jobs.retrieve(gpt_parkcode_model).fine_tuned_model
    endpoint_model = client.fine_tuning.jobs.retrieve(gpt_endpoint_model).fine_tuned_model

    # Predict endpoint and parkcode
    max_tokens = 3
    endpoint = handle_query(query,endpoint_model,client,max_tokens).replace('endpoint: ','')
    max_tokens = 5
    parkcode = handle_query(query,parkcode_model,client,max_tokens).replace('parkcode: ','')

    return endpoint, parkcode

def api_call(query):
    """
    Use to get all data from endpoint without specific processing

    endpoint: The API endpoint to call
    params: The param dict to pass through the API call
    * ChatGPT was used to create the pagination process for parsing the API data.
    """

    endpoint, parkcode = get_params(query)
    responses = []
    limit = 50  # Number of results per page, maximum allowed by NPS API
    start = 0   # Initial starting point for pagination
    
    while True:
        params = {'api_key': config['nps_api_key'],
                  'parkCode': parkcode,
                  'limit' : limit,
                  'start' : start,
                }
        
        if endpoint == 'fees':
            endpoint = 'feespasses'
        request = requests.get(f"{api_base_url}{endpoint}", params=params)
        request_data = request.json()

        # Limit park data to necessary fields
        if endpoint == 'parks':
            responses.extend([
                {
                    'fullName': park['fullName'],
                    'parkCode': park['parkCode'],
                    'state': park['states'],
                    'addresses': park.get('addresses', []),
                    'description': park['description']
                } for park in request_data['data']
            ])
        else:
            for record in request_data['data']:
                responses.extend([record])
        
        # Move to the next page
        start += limit
        
        # Break the loop if all responses have been retrieved
        if int(start) >= int(request_data['total']):
            break

    # Parse responses into appropriate output
    if endpoint == 'activities':
        output = [item['name'] for item in responses]
    elif endpoint == 'parks':
        temp_df = pd.DataFrame(responses[0])    
        addresses_df = pd.json_normalize(temp_df['addresses'])
        output = pd.concat([temp_df.drop(columns=['addresses']), addresses_df], axis=1) 
    else:
        output = pd.DataFrame(responses)    

    return output

