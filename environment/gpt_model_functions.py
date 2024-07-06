import pandas as pd 
import json
import requests
from openai import OpenAI

from environment import env
config = env.env()

api_base_url = 'https://developer.nps.gov/api/v1/'
parkcode_to_park = pd.read_csv(config['root']+'parkcode_to_park.csv')
parkcode_to_park = dict(zip(parkcode_to_park['parkCode'], parkcode_to_park['fullName']))

state_to_code = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}
    
# invert the dictionary
code_to_stat = dict(map(reversed, state_to_code.items()))

def statecode_mapping(state_code):
    return code_to_stat[state_code]

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
    gpt_intent_model = config['gpt_intent_model']
    intents = ['description','address','state','fullname','alerts','amenities','events','feespass']

    # Load models from OpenAI
    parkcode_model = client.fine_tuning.jobs.retrieve(gpt_parkcode_model).fine_tuned_model
    endpoint_model = client.fine_tuning.jobs.retrieve(gpt_endpoint_model).fine_tuned_model
    intent_model = client.fine_tuning.jobs.retrieve(gpt_intent_model).fine_tuned_model

    # Predict endpoint and parkcode
    max_tokens = 3
    endpoint = handle_query(query,endpoint_model,client,max_tokens).replace('endpoint: ','')
    max_tokens = 5
    parkcode = handle_query(query,parkcode_model,client,max_tokens).replace('parkcode: ','')
    max_tokens = 1
    if handle_query(query,intent_model,client,max_tokens) in intents:
        intent = handle_query(query,intent_model,client,max_tokens)
    elif handle_query(query,intent_model,client,2) in intents:
        intent = handle_query(query,intent_model,client,2)
    elif handle_query(query,intent_model,client,3) in intents:
        intent = handle_query(query,intent_model,client,3)

    return endpoint, parkcode, intent

def api_call(query):
    """
    Use to get all data from endpoint without specific processing

    endpoint: The API endpoint to call
    params: The param dict to pass through the API call
    * ChatGPT was used to create the pagination process for parsing the API data.
    """

    endpoint, parkcode, intent = get_params(query)
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
    if endpoint == 'parks':
        temp_df = pd.DataFrame(responses[0])    
        addresses_df = pd.json_normalize(temp_df['addresses'])
        output = pd.concat([temp_df.drop(columns=['addresses']), addresses_df], axis=1) 
        if intent == 'state':
            output = f"{output['fullName'][0]} is located in {statecode_mapping(output['state'][0])}"
        if intent == 'address':
            output = f"{output['fullName'][0]} is located at {output['line1'][0]} " + (f"{output['line2'][0]} " if output['line2'][0] else "") + f"in {output['city'][0]}, {statecode_mapping(output['state'][0])} {output['postalCode'][0]}"
    else:
        output = pd.DataFrame(responses)    

    return endpoint, parkcode, intent, output

