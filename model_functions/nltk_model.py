#IMPORTS
import pandas as pd
import requests
import pickle
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import sys
sys.path.insert(0,'../')
from environment import env
config = env.env()

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

#VARIABLES
api_base_url = 'https://developer.nps.gov/api/v1/'
park_csv_path = '../02_nps_api_data/park_to_parkcode.csv'


#NLTK CLASS DEFINITION
class NLTKModelFunctions:
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
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))
        
        for index, row in park_df.iterrows():
            tokens = word_tokenize(row['fullName'].lower())
            tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalpha() and token not in stop_words]
            normalized_park_name = ' '.join(tokens)
            park_codes[normalized_park_name] = row['parkCode']
        
        return park_codes

    def preprocess_text(self, text):
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        return ' '.join(tokens)

    def predict_intent(self, query):
        preprocessed_query = self.preprocess_text(query)
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
        preprocessed_query = self.preprocess_text(query)
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))
        for park_name, park_code in self.park_codes.items():
            tokens = word_tokenize(park_name)
            tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalpha() and token not in stop_words]
            normalized_park_name = ' '.join(tokens)
            if normalized_park_name in preprocessed_query:
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

#NLTK MODEL
nltk_model_functions = NLTKModelFunctions(config, park_csv_path)
