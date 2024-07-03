| Order | Parent Folder |             File Name               |                         Description                   | 
|-------|---------------|-------------------------------------|-------------------------------------------------------|
| 1     | Data_API      | helper_functions/nps_parks_root.py  | List of root park names                               |
| 2     | GPTModel      | helper_functions/park_code_model.py | Creates a logistic regression model to predict the park code based on a user query. This model is only used in the synthetic data creation process                               |
| 3     | environment      | helper_functions.py              | Prepare synthetic data for GPT consumption            |
| 4     | environment      | gpt_model_functions.py           | Use GPT model to make API calls provided a user query |