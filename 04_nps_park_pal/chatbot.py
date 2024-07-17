
import sys
sys.path.insert(0,'../')
from environment import env
from nps_model_functions import *
config = env.env()

import gradio as gr

def chatbot(user_input):
    if not user_input:
        return "Please provide a message."
    try:
        # Calls the OpenAI Fine-tuned GPT models (each run will charge the account)
        output = nps_model_functions.api_call(user_input)
    except:
        output = "I specialize only in queries related to amenities, events, alerts, park fees, park locations, and park descriptions. Please clarify your question."
    return output

iface = gr.Interface(
    fn=chatbot,
    inputs="text",
    outputs="text",
    title="Park Pal Chatbot",
    description="Ask me about amenities, events, alerts, park fees, park locations, and park descriptions in National Parks."
)

iface.launch()