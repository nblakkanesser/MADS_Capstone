# %% [markdown]
# #### Define Imports

# %%
import requests
import pandas as pd 
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


# %% [markdown]
# #### Define Functions

# %%
def generate_synthetic_states(raw_queries,state_codes,state_names,state_abbreviations):
    """
    Creates synthetic query data that will be used as training data for a model that identifies the state being asked about in a query.

    raw_queries: List of queries to loop through and create data for.
    state_codes: State codes associated with the state name.
    state_names: List of states to create the queries for.
    state_abbreviations: List of state abbreviations to create the queries for.
    """
    queries = []
    query_state = []
    query_state_code = []
    for state_name, state_code, state_abbreviation in zip(state_names, state_codes, state_abbreviations):
        for query in raw_queries:
            output = query.format(entity=state_name)
            queries.append(output)
            query_state.append(state_name)
            query_state_code.append(state_code)

            output = query.format(entity=state_abbreviation)
            queries.append(output)
            query_state.append(state_abbreviation)
            query_state_code.append(state_code)
        
    data = {
    'query': queries,
    'state_name': query_state,
    'state_code': query_state_code
    }

    return data


# %%
def map_state_code(user_input, model, vectorizer):
    """
    Map user input to the correct state code using the trained model.

    user_input: The query provided by the user.
    model: Trained classification model.
    vectorizer: Fitted vectorizer for text processing.
    """
    # Transform the user input
    user_input_vectorized = vectorizer.transform([user_input])
    
    # Predict the state code
    predicted_state_code = model.predict(user_input_vectorized)[0]
    
    return predicted_state_code

# %%
def train_model(synthetic_state_data):
    # Vectorize the text data
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(synthetic_state_data['query'])
    y = synthetic_state_data['state_code']

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a logistic regression model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    return model, vectorizer

# %% [markdown]
# #### Define Variables

# %%
raw_queries = ['Which parks are in {entity}?', 
    'Parks in {entity}', 
    'Find parks in {entity}', 
    '{entity} parks',
    'List parks in {entity}',
    'What parks can I visit in {entity}?',
    'Show me parks located in {entity}',
    'Explore {entity} parks',
    'Are there any parks around {entity}?',
    'Tell me about the parks near {entity}',
    'Show parks within {entity}',
    'Which national parks are near {entity}?',
    'Locate parks in {entity}',
    'What are the top parks in {entity}?',
    'Give me information about {entity} parks',
    'Search for parks near {entity}',
    'Find national parks in {entity}',
    'What are the names of parks in {entity}?',
    'I want to know about parks around {entity}',
    'Which parks are in {entity}?', 
    'Parks in {entity}', 
    'Find parks in {entity}', 
    '{entity} parks',
    'List parks in {entity}',
    'What parks can I visit in {entity}?',
    'Show me parks located in {entity}',
    'Explore {entity} parks',
    'Are there any parks around {entity}?',
    'Tell me about the parks near {entity}',
    'Show parks within {entity}',
    'Which national parks are near {entity}?',
    'Locate parks in {entity}',
    'What are the top parks in {entity}?',
    'Give me information about {entity} parks',
    'Search for parks near {entity}',
    'Find national parks in {entity}',
    'What are the names of parks in {entity}?',
    'I want to know about parks around {entity}',
    'Are there any good parks near {entity}?']

state_codes = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
state_names = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", 
                "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", 
                "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", 
                "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", 
                "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", 
                "New Hampshire", "New Jersey", "New Mexico", "New York", 
                "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", 
                "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
                "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", 
                "West Virginia", "Wisconsin", "Wyoming"]
state_abbreviations = ["Ala.", "Alaska", "Ariz.", "Ark.", "Calif.", "Colo.", 
                        "Conn.", "Del.", "Fla.", "Ga.", "Hawaii", "Idaho", "Ill.", 
                        "Ind.", "Iowa", "Kan.", "Ky.", "La.", "Maine", "Md.", 
                        "Mass.", "Mich.", "Minn.", "Miss.", "Mo.", "Mont.", "Neb.", 
                        "Nev.", "N.H.", "N.J.", "N.M.", "N.Y.", "N.C.", "N.D.", 
                        "Ohio", "Okla.", "Ore.", "Pa.", "R.I.", "S.C.", "S.D.", 
                        "Tenn.", "Tex.", "Utah", "Vt.", "Va.", "Wash.", "W.Va.", 
                        "Wis.", "Wyo."]

# %%
def trained_model():
    synthetic_state_data = generate_synthetic_states(raw_queries,state_codes,state_names,state_abbreviations)
    model, vectorizer = train_model(synthetic_state_data)
    return model, vectorizer



# %%
