### Environment Notebook Setup Procedure

The notebooks in this repo use a custom environment function to set user specific values such as secrets, API keys, and folder paths. Users can add a env.py to the environment folder using the following structure to initialize their environment values.

```python
def env():
	dict = {'nps_api_key': '', # The users specific NPS API key. The key can be requested here: https://www.nps.gov/subjects/developer/get-started.htm
		 'gpt_api_key': '', # The users specific OpenAI API key. The key can be requested here: https://platform.openai.com/api-keys
		 'gpt_parkcode_model': '', # The OpenAI Job ID for the parkcode model fine tuned using the GPT Model notebooks.
		 'gpt_endpoint_model': '', # The OpenAI Job ID for the endpoint model fine tuned using the GPT Model notebooks.
		 'gpt_intent_model':'',# The OpenAI Job ID for the intent model fine tuned using the GPT Model notebooks.
		 }
	return dict