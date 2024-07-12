| Order | Parent Folder |             File Name               |                         Description                   | 
|-------|---------------|-------------------------------------|-------------------------------------------------------|
| 1     | 02_nps_api_data | helper_functions/nps_parks_root.py  | List of root park names                               |
| 2     | GPTModel      | helper_functions/park_code_model.py | Creates a logistic regression model to predict the park code based on a user query. This model is only used in the synthetic data creation process                               |
| 3     | nps_model_functions      | helper_functions.py              | Prepare synthetic data for GPT consumption            |
| 4     | nps_model_functions      | gpt_model_functions.py           | Use GPT model to make API calls provided a user query |
| 5     | 04_nps_park_pal      | templates/index.html             | Includes the code to create a simple web-based chat interface for the "National Parks Chatbot: Park Pal."  |