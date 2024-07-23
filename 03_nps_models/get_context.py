#IMPORTS
import pandas as pd
import requests
import sys

sys.path.insert(0,'../')
from environment import env
config = env.env()


#VARIABLES
api_base_url = 'https://developer.nps.gov/api/v1/'
#park_csv_path = '../02_nps_api_data/park_to_parkcode.csv'
#parkcode_to_park = pd.read_csv('../02_nps_api_data/parkcode_to_park.csv')
#parkcode_to_park = dict(zip(parkcode_to_park['parkCode'], parkcode_to_park['fullName']))


def api_call(endpoint, parkcode, intent,parse = True):
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
    response = api_call(endpoint, parkcode, intent)
    #context = parse_endpoint(endpoint, parkcode, intent, response)
    
    return response#context

