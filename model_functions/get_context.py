#IMPORTS
import pandas as pd
import requests
from datetime import datetime
import sys

sys.path.insert(0,'../')
from environment import env
config = env.env()


#VARIABLES
api_base_url = 'https://developer.nps.gov/api/v1/'
parkcode_to_park = pd.read_csv('../02_nps_api_data/parkcode_to_park.csv')
parkcode_to_park = dict(zip(parkcode_to_park['parkCode'], parkcode_to_park['fullName']))

# * The mapping dictionary below was created by rogerallen and found at: https://gist.github.com/rogerallen/1583593
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


#FUNCTIONS

def call_api(endpoint, parkcode, intent,parse = True):
    """
    Use to get all data from endpoint without specific processing

    query: A user query.
    parse: Whether or not to call the parse_endpoint function. 
    * ChatGPT was used to create the pagination process for parsing the API data.
    """

    response = []
    limit = 50  # Number of results per page, maximum allowed by NPS API
    start = 0   # Initial starting point for pagination
    
    while True:
        params = {'api_key': config['nps_api_key'],
                  'parkCode': parkcode,
                  'limit' : limit,
                  'start' : start,
                }
        
        request = requests.get(f"{api_base_url}{endpoint}", params=params)
        request_data = request.json()

        # Limit park data to necessary fields
        for record in request_data['data']:
            response.extend([record])
        
        # Move to the next page
        start += limit
        
        # Break the loop if all responses have been retrieved
        if int(start) >= int(request_data['total']):
            break

    return response


def get_context(query, model):
    """Given a query and model, returns the response from API call"""
    endpoint, parkcode, intent = model.get_params(query)
    response = call_api(endpoint, parkcode, intent)
    
    return response

#For ChatBot

def parsed_context(endpoint, parkcode, intent):
    """Takes direct context from API call and extracts relevant bit of context to be used as ground truth for model testing
        Input: api_context = unparsed results from NPS API call
            intent = intent of query
        Output: """
    api_context = call_api(endpoint, parkcode, intent)
    if len(api_context)==0:
        return f'No {intent} information found'

    def items(api_cont, tags):
        """For calls that return more than 1 item (alerts, events, etc) returns a concatonated list"""
        context = []
        for item in api_cont:
            for tag in tags:
                context.append(str(item.get(tag, ''))),
        context = [x for x in context if len(x)>0]
        return ", ".join(context)
        

    parser = {
        'description': api_context[0].get('description', ''),
        'fullname': api_context[0].get('fullName', ''),
        'alerts': items(api_context, ['title', 'description']),
        'events': items(api_context, ['title', 'description', 'location']),     
        'feespass': " ".join([['Interagency Pass is accepted' if api_context[0].get('isInteragencyPassAccepted.','')==True  else 'Interagency Pass is not accepted.'][0],
                              items(api_context, ['entranceFeeDescription', 'entrancePassDescription','timedEntryDescription']),
                               items(api_context[0].get('fees',''), ['entranceFeeType', 'cost', 'description']),]),
        'amenities': items(api_context,['name']),
        'address': items(api_context[0].get('addresses',''), ['line1', 'city', 'stateCode', 'postalCode','provinceTerritoryCode']),
        'state': code_to_state.get(api_context[0].get('state', ''), '')
    }
    context = parser[intent]

    return context

'''def api_call_test(endpoint, parkcode, intent,parse = True):
    """
    Use to get all data from endpoint without specific processing

    query: A user query.
    parse: Whether or not to call the parse_endpoint function. 
    * ChatGPT was used to create the pagination process for parsing the API data.
    """

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


    return responses'''