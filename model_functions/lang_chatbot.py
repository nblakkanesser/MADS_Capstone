from langchain_openai import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser

import sys
sys.path.insert(0,'../')
from environment import env
config = env.env()

OPENAI_API_KEY = config['gpt_api_key']

chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0,api_key  = OPENAI_API_KEY)
output_parser = StrOutputParser()

nps_template_str = """You're an assistant knowledgeable about national parks. 
Only answer national park related questions. Use the following context to answer these questions. Answer given question strictly based on context.
This information is in a dictionary format.

{context}
"""
nps_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"],
        template=nps_template_str,
    )
)

nps_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["question"],
        template="{question}",
    )
)
messages = [nps_system_prompt, nps_human_prompt]

nps_prompt_template = ChatPromptTemplate(
    input_variables=["context", "question"],
    messages=messages,
)

nps_chain = nps_prompt_template | chat_model | output_parser