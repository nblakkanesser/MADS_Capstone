import pandas as pd 
import json
from openai import OpenAI
from sklearn.model_selection import train_test_split

from environment import env
config = env.env()

api_base_url = 'https://developer.nps.gov/api/v1/'
client = OpenAI(api_key  = config['gpt_api_key'])

def create_prompt_response(row, target):
    """
    Parses the synthetic data into GPT format
    """
    if target == 'endpoint':
        dict = {'prompt': row['query'],
                'completion':f"endpoint: {row['api_call.endpoint']}"}
    elif target == 'parkcode':
        dict = {'prompt': row['query'],
                'completion':f"parkcode: {row['api_call.parkCode']}"}
    elif target == 'intent':
        dict = {'prompt': row['query'],
                'completion':f"{row['intent']}"}
    return dict

def save_to_jsonl(dataframe, filename,target):
    """
    Writes record to json with correct GPT format
    * ChatGPT assisted in writing this function
    """
    with open(filename, 'w') as f:
        for _, row in dataframe.iterrows():
            example = create_prompt_response(row,target)
            json.dump(example, f)
            f.write('\n')

def split_synthetic_data(synthetic_queries_df,target):
    # Train/validation split
    train_df, val_df = train_test_split(synthetic_queries_df, test_size=0.2, random_state=42)
    #print(len(train_df),len(val_df))

    # Saves training and validation data to json for ingestion by OpenAI GPT
    save_to_jsonl(train_df, f'{target}_train_data.jsonl', target)
    save_to_jsonl(val_df, f'{target}_val_data.jsonl', target)


def finetune_gpt_model(target):
  # Upload a file that can be used across various endpoints. Individual files can be up to 512 MB, and the size of all files uploaded by one organization can be up to 100 GB.
    # Documentation: https://platform.openai.com/docs/api-reference/files/create
  train_file =  client.files.create(
    file=open(f'{target}_train_data.jsonl', "rb"),
    purpose="fine-tune"
  )

  val_file = client.files.create(
    file=open(f'{target}_val_data.jsonl', "rb"),
    purpose="fine-tune"
  )

  # Retrieve file id to be used in fine tuning job
  train_file_id = train_file.id
  val_file_id = val_file.id

  # Creates a fine-tuning job which begins the process of creating a new model from a given dataset.
    # Documentation: https://platform.openai.com/docs/api-reference/fine-tuning/create
  fine_tune = client.fine_tuning.jobs.create(
    # The Davinci model was selected for its performance as a completion model over using a chat model based on our use case.
    # We also tried using the gpt-3.5-turbo and we were unable to get the model to complete after an hour of training.
    # Conversely, the davinci model averaged a 20 minute training period.
    model="davinci-002",
    training_file=train_file_id,
    validation_file=val_file_id,
    seed = 42,
    suffix = f'nps_model_{target}'
  )
  # The fine tune id needs to be retained and set in the environment file to be used when calling the fine-tuned model.
  fine_tune_id = fine_tune.id
  return fine_tune_id