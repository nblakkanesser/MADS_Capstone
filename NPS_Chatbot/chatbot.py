from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory.buffer import ConversationBufferMemory
import chainlit as cl
from langchain.chains import APIChain

import sys
sys.path.insert(0,'../')
import pandas as pd
from environment import env
from environment import gpt_model_functions
config = env.env()

OPENAI_API_KEY = config['gpt_api_key']

assistant_template = """
You are an national parks service assistant chatbot named "Park Pal". Your expertise is 
exclusively in providing information directly from the national parks service API. This includes queries related to amenities, events, alerts, park fees, park locations, and park descriptions. You do not provide information outside of this 
scope. If a question is not about an API endpoint listed previously, respond with, "I specialize only in queries related to amenities, events, alerts, park fees, park locations, and park descriptions." 
Question: {question} 
Answer:"""

prompt_template = PromptTemplate(
    input_variables=["chat_history", "question"],
    template=assistant_template
)

@cl.on_chat_start
def quey_llm():
    llm = OpenAI(model='gpt-3.5-turbo-instruct',
             temperature=0.7,
             openai_api_key = OPENAI_API_KEY)
    
    conversation_memory = ConversationBufferMemory(memory_key="chat_history",
                                                   max_len=50,
                                                   return_messages=True,
                                                   )
    llm_chain = LLMChain(llm=llm, 
                         prompt=prompt_template,
                         memory=conversation_memory)
    
    cl.user_session.set("llm_chain", llm_chain)

@cl.on_message
async def query_llm(message: cl.Message):
    llm_chain = cl.user_session.get("llm_chain")
    
    response = await llm_chain.acall(message.content, 
                                     callbacks=[
                                         cl.AsyncLangchainCallbackHandler()])
    
    await cl.Message(response["text"]).send()
