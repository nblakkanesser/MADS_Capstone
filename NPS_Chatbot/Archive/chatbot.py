import sys
sys.path.insert(0,'../')
from environment import NPS_API
from environment import gpt_model_functions
from environment import env
config = env.env()

OPENAI_API_KEY = config['gpt_api_key']

from langchain_openai import OpenAI 
import chainlit as cl
from langchain.chains import LLMChain, APIChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory.buffer import ConversationBufferMemory
from langchain.chains import APIChain


assistant_template = """
You are an national parks service assistant chatbot named "Park Pal". Your expertise is 
exclusively in providing information directly from the national parks service API. This includes queries related to amenities, events, alerts, park fees, park locations, and park descriptions. You do not provide information outside of this 
scope. If a question is not about an API endpoint listed previously, respond with, "I specialize only in queries related to amenities, events, alerts, park fees, park locations, and park descriptions." 
Question: {question} 
Answer:"""

api_url_template = """
Given the following API Documentation for the national parks service API: {api_docs}
Your task is to interpret the data returned from the API to answer 
the user's question, ensuring the 
answer includes only necessary information.
Question: {question}
"""
api_url_prompt = PromptTemplate(input_variables=['api_docs', 'question'],
                                template=api_url_template)

api_response_template = """"
With the API Documentation for the national parks service API: {api_docs} 
and the specific user question: {question} in mind,
and given the variable api_url: {api_url} for querying,
here is the response from the national parks service's API: {api_response}. 
Please provide a summary that directly addresses the user's question, 
omitting technical details like response format, and 
focusing on delivering the answer with clarity and conciseness, 
as if the national parks service itself is providing this information.
Summary:
"""
api_response_prompt = PromptTemplate(input_variables=['api_docs', 
                                                      'question', 
                                                      'api_url',
                                                      'api_response'],
                                     template=api_response_template)


@cl.on_chat_start
def setup_multiple_chains():
    llm = OpenAI(model='gpt-3.5-turbo-instruct',
             temperature=0,
             openai_api_key = OPENAI_API_KEY)
    conversation_memory = ConversationBufferMemory(memory_key="chat_history",
                                                   max_len=200,
                                                   return_messages=True,
                                                   )
    llm_chain = LLMChain(llm=llm, prompt=assistant_template, memory=conversation_memory)
    cl.user_session.set("llm_chain", llm_chain)

    api_chain = APIChain.from_llm_and_api_docs(
        llm=llm,
        api_docs=NPS_API.api_docs(),
        api_url_prompt=api_url_prompt,
        api_response_prompt=api_response_prompt,
        verbose=True
    )
    cl.user_session.set("api_chain", api_chain)

@cl.on_message
async def handle_message(message: cl.Message):
    user_message = message.content.lower()
    api_url,endpoint = gpt_model_functions.create_url(user_message)
    llm_chain = cl.user_session.get("llm_chain")
    api_chain = cl.user_session.get("api_chain")
    
    if endpoint in ['alerts']:
        # If endpoint is specified endpoint use api_chain
        response = await api_chain.acall(user_message, 
                                         callbacks=[cl.AsyncLangchainCallbackHandler()])
    else:
        # Default to llm_chain for handling general queries
        response = await llm_chain.acall(user_message, 
                                         callbacks=[cl.AsyncLangchainCallbackHandler()])
    response_key = "output" if "output" in response else "text"
    await cl.Message(response.get(response_key, "")).send()