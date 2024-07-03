Place Holder
hugging face - chunking strategies
embedding the chunks into vectors
chroma (vector store) 
retrieval method - API calls/
-> question -> chunks from store -> LLM -> answer question based on context

Can we have chat gpt create the API call string?
->prompt and examples

Separate prompt for Park to ParkCode?

Evaluation
RAGAS - for RAG evaluation, explore what types of evaluation, retrieval-focused
Correct generation - some manual evaluation may be necessary 

Evaluate chatGpt vs a traditional NLP key-word matching on the same queries
Set up baseline architecture for experimentation


#Streamlit user interface
# retieval augmented generation
# chunking
# hugging face python package for chunking
# then embedding (vector store: chroma)
# retieval methodology (retriever, embeds question, then pulls chunks to the llm )
# few shot