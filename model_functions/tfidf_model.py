#IMPORTS
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import sys
sys.path.insert(0,'../')
from environment import env


#VARIABLES
config = env.env()

#Inputs
api_base_url = 'https://developer.nps.gov/api/v1/'
park_csv_path = '../02_nps_api_data/park_to_parkcode.csv'
training_queries = '../02_nps_api_data/synthetic_queries.csv'

# Outputs
#trained_model = 'tfidf_model.pkl'


#TFIDF MODEL DEFINITION
class TfidfClassifier:
    def __init__(self, config, park_csv_path):
        self.config = config
        self.intent_clf = GaussianNB()
        self.intent_vectorizer = TfidfVectorizer()
        self.parkcode_clf = GaussianNB()
        self.parkcode_vectorizer = TfidfVectorizer()

    def fit(self, path):
        """Loads training data into a df + uses tfidf vectorized queries to fit models:
            intent_clf predicts intent
            parkcode_ clf predicts parkcode
        """
        df = pd.read_csv(path)
        query = df['query']
    
        X_train = self.intent_vectorizer.fit_transform(query).toarray()
        y_train = df['intent']
        self.intent_clf.fit(X_train, y_train)

        X_train = self.parkcode_vectorizer.fit_transform(query).toarray()
        y_train = df['api_call.parkCode']
        self.parkcode_clf.fit(X_train, y_train)

        return self.intent_clf, self.parkcode_clf
        

    def get_params(self, query):
        """Given a query input, uses intent_clf and parkcode_clf to predict
            intent and parkcode of query, and corresponting api endpoint
        """
        
        intent_vec = self.intent_vectorizer.transform([query]).toarray()
        parkcode_vec = self.parkcode_vectorizer.transform([query]).toarray()

        parkcode = self.parkcode_clf.predict(parkcode_vec)
        intent = self.intent_clf.predict(intent_vec)
        
        endpoint_mapping = {
            'description': 'parks',
            'address': 'parks',
            'state': 'parks',
            'alerts': 'alerts',
            'amenities': 'amenities',
            'events': 'events',
            'feespass': 'feespasses'
        }

        endpoint = endpoint_mapping.get(intent[0], 'parks')

        return endpoint, parkcode[0], intent[0]
    
#Train and Store Model    
tfidf_model = TfidfClassifier(config, park_csv_path)
tfidf_model.fit(training_queries)
#pickle.dump(tfidf_model, open(trained_model, 'wb'))
