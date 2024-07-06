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
code_to_state = dict(map(reversed, state_to_code.items()))

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
    #The intents dont have a uniform number of tokens and this was my solution (I'd like to improve this logic)
    if handle_query(query,intent_model,client,max_tokens) in intents:
        intent = handle_query(query,intent_model,client,max_tokens)
    elif handle_query(query,intent_model,client,2) in intents:
        intent = handle_query(query,intent_model,client,2)
    elif handle_query(query,intent_model,client,3) in intents:
        intent = handle_query(query,intent_model,client,3)

    return endpoint, parkcode, intent

def parse_endpoint(endpoint, parkcode, intent, responses):
    parkname = parkcode_to_park[parkcode]
    # Parse responses into appropriate output
    if endpoint == 'parks':
        # The address field of the parks endpoint comes in as a dictionary and the three lines below normalize the data into separate columns.
        temp_df = pd.DataFrame(responses[0])    
        addresses_df = pd.json_normalize(temp_df['addresses'])
        responses_df = pd.concat([temp_df.drop(columns=['addresses']), addresses_df], axis=1) 

        # Map state code to state name
        state_name = code_to_state[responses_df['state'][0]]

        # Answers question: which state is the park in?
        if intent == 'state':
            output = f"{responses_df['fullName'][0]} is located in {state_name}"
        # Answers question: what is the park address?
        if intent == 'address':
            output = f"{responses_df['fullName'][0]} is located at {responses_df['line1'][0]} " + (f"{responses_df['line2'][0]} " if responses_df['line2'][0] else "") + f"in {responses_df['city'][0]}, {state_name} {responses_df['postalCode'][0]}"
    # Have to add desciption and full name

    elif endpoint == 'alerts':
        # The alerts endpoint is straight forward but there may be multiple alerts so this function returns a count of the active alerts and then lists the alerts. 
        responses_df = pd.DataFrame(responses) 
        if len(responses_df) > 0:
            output = f'There are {len(responses_df)} active alerts for {parkname}: \n '
            # List each alert
            for index, row in responses_df.iterrows():
                output += f"Alert {index+1}: {row['description']}\n "
        else:
            # When there are no active alerts return the following:
            output = f'There are no active alerts for {parkname}'
    else:
        output = pd.DataFrame(responses)   
    
    return output


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

    output = parse_endpoint(endpoint, parkcode, intent, responses)

    return endpoint, parkcode, intent, output

