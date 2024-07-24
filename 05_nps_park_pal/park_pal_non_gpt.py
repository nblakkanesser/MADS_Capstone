#Hosting Locally:
import sys
sys.path.insert(0,'../')
from environment import env
from model_functions.gpt_model_functions import *
config = env.env()

from flask import Flask, request, jsonify, render_template
# *ChatGPT created the following flask application.
# ChatGPT also constructed the index.html file.
# Our team customized the style code within the index.html.
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"response": "Please provide a message."})

    try:
        # Calls the OpenAI Fine-tuned GPT models (each run will charge the account)
        output = api_call(user_input)
    except:
        output = "I specialize only in queries related to amenities, events, alerts, park fees, park locations, and park descriptions. Please clarify your question."
    return jsonify({"response": output})

if __name__ == "__main__":
    app.run(port=8000)