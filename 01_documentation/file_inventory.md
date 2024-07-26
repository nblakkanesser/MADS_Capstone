| Order |   Parent Folder     |             File Name               |                         Description                                      | 
|-------|---------------------|-------------------------------------|--------------------------------------------------------------------------|
| 1     | 02_nps_api_data     | helper_functions/nps_parks_root.py  | List of root park names                                                  |
| 2     | 02_nps_api_data     | helper_functions/park_code_model.py | Creates a logistic regression model to predict the park code based on a user query. This model is only used in the synthetic data creation process           |
| 3     | 02_nps_api_data     | park_to_parkcode.csv                | Mapping dictionary for full park name to parkcode                        |
| 4     | 02_nps_api_data     | park_to_root.csv                    | Mapping dictionary for full park name to abbreviated park name           |
| 5     | 02_nps_api_data     | parkcode_to_park.csv                | Mapping dictionary for parkcode to full park name                        |
| 6     | 02_nps_api_data     | synthetic_queries.csv               | Training and validation synthetic queries                                |
| 7     | 02_nps_api_data     | testing_queries.csv                 | Testing synthetic queries                                                |
| 8     | 02_nps_api_data     | nps_monthly_visits.csv              | NPS monthly visit data by region 2023                                    |
| 9     | 02_nps_api_data     | nps_top_parks.csv                   | Top 10 National Parks by visits in 2023                                  |
| 10    | 02_nps_api_data     | nps_visitations_2023.csv            | Data collected from https://irma.nps.gov/Portal/                         |
| 11    | 02_nps_api_data     | nps_yearly_visits.csv               | 2023 yearly visit data by region                                         |
| 12    | 03_nps_models       | endpoint_train_data.jsonl           | Training prompt and completion data for fine-tuning GPT endpoint model   |
| 13    | 03_nps_models       | endpoint_val_data.jsonl             | Validation prompt and completion data for fine-tuning GPT endpoint model |
| 14    | 03_nps_models       | intent_train_data.jsonl             | Training prompt and completion data for fine-tuning GPT intent model     |
| 15    | 03_nps_models       | intent_val_data.jsonl               | Validation prompt and completion data for fine-tuning GPT intent model   |
| 16    | 03_nps_models       | parkcode_train_data.jsonl           | Training prompt and completion data for fine-tuning GPT parkcode model   |
| 17    | 03_nps_models       | parkcode_val_data.jsonl             | Validation prompt and completion data for fine-tuning GPT parkcode model |
| 18    | 03_nps_models       | tfidf_model.pkl                     | The TF-IDF model trained on the synthetic data                           |
| 20    | 04_nps_evaluation   | test_data.pkl                       | [INSERT INFORMATION HERE]                      |
| 21    | 05_nps_park_pal     | templates/index.html                | Includes the code to create a simple web-based chat interface for the "National Parks Chatbot: Park Pal."  |
| 22    | 05_nps_park_pal     | lang_chatbot.py                     | [INSERT INFORMATION HERE]                      |
| 23    | 05_nps_park_pal     | park_pal_non_gpt.py                 | [INSERT INFORMATION HERE]                      |
| 24    | model_functions     | get_context.py                      | [INSERT INFORMATION HERE]                      |
| 25    | model_functions     | gpt_model_functions.py              | Use GPT model to make API calls provided a user query                    |
| 26    | model_functions     | helper_model_functions.py           | Prepare synthetic data for GPT consumption and fine-tune models          |
| 27    | model_functions     | nltk_model.py                       | [INSERT INFORMATION HERE]                      |
| 28    | model_functions     | non_gpt_model_functions.py          | [INSERT INFORMATION HERE]                      |
| 29    | model_functions     | spacy_model.py                      | [INSERT INFORMATION HERE]                      |
| 30    | model_functions     | tfidf_model.py                      | [INSERT INFORMATION HERE]                      |
