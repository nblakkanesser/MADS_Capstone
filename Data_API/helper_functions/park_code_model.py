# %% [markdown]
# #### Define Imports

# %%
import requests
import pandas as pd 
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,f1_score,roc_auc_score

from helper_functions import *
import sys
sys.path.insert(0,'../')
from environment import env

config = env.env()
api_key = config['nps_api_key']
api_base_url = 'https://developer.nps.gov/api/v1/'


# %% [markdown]
# #### Define Functions

# %%
def get_parks(params):
    """
    Use to find a list of all park names, codes, states, addresses and descriptions from the NPS parks endpoint.
    Can also be used to find specific park information.
    
    api_key: Personal API key to use in request
    """
    parks = []
    limit = 50  # Number of results per page, maximum allowed by NPS API
    start = 0   # Initial starting point for pagination
    
    while True:
        params = {
            'api_key': api_key,
            'limit': limit,
            'start': start
        }
        
        response = requests.get(f"{api_base_url}parks", params=params)
        data = response.json()
        
        parks.extend([
            {
                'fullName': park['fullName'],
                'parkCode': park['parkCode'],
                'state': park['states'],
                'addresses': park.get('addresses', []),
                'description': park['description']
            } for park in data['data']
        ])
        
        # Move to the next page
        start += limit
        
        # Break the loop if all parks have been retrieved
        if int(start) >= int(data['total']):
            break
    
    return parks

# %%
def generate_synthetic_parks(raw_queries,park_codes,parks,park_abbreviations):
    """
    Creates synthetic query data that will be used as training data for a model that identifies the state being asked about in a query.

    raw_queries: List of queries to loop through and create data for.
    park_codes: Park codes associated with the park name.
    parks: List of parks to create the queries for.
    park_abbreviations: List of park abbreviations to create the queries for.
    """
    queries = []
    query_park_name = []
    query_park_code = []
    for park_name, park_code, park_abbreviation in zip(parks, park_codes, park_abbreviations):
        for query in raw_queries:
            output = query.format(entity=park_name)
            queries.append(output)
            query_park_name.append(park_name)
            query_park_code.append(park_code)

            output = query.format(entity=park_abbreviation)
            queries.append(output)
            query_park_name.append(park_name)
            query_park_code.append(park_code)
        
    data = {
    'query': queries,
    'parks': query_park_name,
    'park_codes': query_park_code
    }

    return data


# %%
def map_park_code(user_input, model, vectorizer):
    """
    Map user input to the correct park code using the trained model.

    user_input: The query provided by the user.
    model: Trained classification model.
    vectorizer: Fitted vectorizer for text processing.
    """
    # Transform the user input
    user_input_vectorized = vectorizer.transform([user_input])
    
    # Predict the state code
    predicted_park_code = model.predict(user_input_vectorized)[0]
    
    return predicted_park_code

# %%
def train_model(synthetic_park_data):
    # Vectorize the text data
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(synthetic_park_data['query'])
    y = synthetic_park_data['park_codes']

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a logistic regression model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    return model, vectorizer

# %% [markdown]
# #### Define Variables

# %%
parks_df = pd.DataFrame(get_parks({'api_key': api_key}))
parks = parks_df['fullName'].tolist()
park_codes = parks_df['parkCode'].tolist()
park_lookup = dict(zip(parks, park_codes))
park_roots = nps_parks_root.nps_parks_root()

# %%
raw_queries = ['What can I do in {entity}?',
    'Where is {entity} located?',
    'What are the best hiking trails in {entity}?',
    'Are there camping facilities in {entity}?',
    'How do I get to {entity}?',
    'What wildlife can I see in {entity}?',
    'Are there any guided tours available in {entity}?',
    'What is the weather like in {entity}?',
    'Can I bring my pet to {entity}?',
    'Are there any entrance fees for {entity}?',
    'What is the best time of year to visit {entity}?',
    'Tell me about the history of {entity}.',
    'Are there any special events happening at {entity}?',
    'What are the must-see attractions in {entity}?',
    'Can I swim in the lakes or rivers at {entity}?',
    'What are the hours of operation for {entity}?',
    'Is there lodging available inside {entity}?',
    'What are the rules for fishing at {entity}?',
    'Are there any restrictions on photography at {entity}?',
    'Tell me about the geological features of {entity}.']


# %%
def trained_model():
    synthetic_park_data = generate_synthetic_parks(raw_queries,park_codes,parks,park_roots)
    model, vectorizer = train_model(synthetic_park_data)
    return model, vectorizer



