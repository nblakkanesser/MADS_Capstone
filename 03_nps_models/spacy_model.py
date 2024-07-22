#IMPORTS
import pandas as pd
import spacy
import pickle
import sys
sys.path.insert(0,'../')
from environment import env

#VARIABLES
config = env.env()
nlp = spacy.load("en_core_web_sm")
api_base_url = 'https://developer.nps.gov/api/v1/'
park_csv_path = '../02_nps_api_data/park_to_parkcode.csv'
model_output = 'spacy_model.pkl'


#SPACY MODEL DEFINITION
class SpaCyModelFunctions:
    def __init__(self, config, park_csv_path):
        self.config = config
        self.park_codes = self.load_park_codes(park_csv_path)

    def load_park_codes(self, park_csv_path):
        """
        Loads park codes from a CSV file into a dictionary.
        
        park_csv_path (str): Path to the CSV file containing park names and their codes.
        """
        park_df = pd.read_csv(park_csv_path)
        park_codes = {}
        
        for index, row in park_df.iterrows():
            tokens = self.preprocess_text(row['fullName'].lower())
            normalized_park_name = ' '.join(tokens)
            park_codes[normalized_park_name] = row['parkCode']
        
        return park_codes

    def preprocess_text(self, text):
        doc = nlp(text)
        return [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]

    def predict_intent(self, query):
        tokens = self.preprocess_text(query.lower())
        preprocessed_query = ' '.join(tokens)
        
        if 'description' in preprocessed_query:
            return 'description'
        elif 'address' in preprocessed_query:
            return 'address'
        elif 'state' in preprocessed_query:
            return 'state'
        elif 'alerts' in preprocessed_query:
            return 'alerts'
        elif 'amenities' in preprocessed_query:
            return 'amenities'
        elif 'events' in preprocessed_query:
            return 'events'
        elif 'fees' in preprocessed_query or 'passes' in preprocessed_query:
            return 'feespass'
        else:
            return 'other'

    def get_park_code(self, query):
        tokens = self.preprocess_text(query.lower())
        preprocessed_query = ' '.join(tokens)
        
        for park_name, park_code in self.park_codes.items():
            if park_name in preprocessed_query:
                return park_code
        return None

    def get_params(self, query):
        intent = self.predict_intent(query)
        park_code = self.get_park_code(query)

        endpoint_mapping = {
            'description': 'parks',
            'address': 'parks',
            'state': 'parks',
            'alerts': 'alerts',
            'amenities': 'amenities',
            'events': 'events',
            'feespass': 'feespasses'
        }

        endpoint = endpoint_mapping.get(intent, 'parks')

        return endpoint, park_code, intent
    
#SPACY MODEL PICKLE
spacy_model_functions = SpaCyModelFunctions(config, park_csv_path)
pickle.dump(spacy_model_functions, open(f'{model_output}', 'wb'))