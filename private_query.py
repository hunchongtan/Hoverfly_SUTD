"""
Remember to install packages before starting!
pip install langchain==0.1.9 chromadb==0.4.24 langchain-openai==0.0.8
"""

import os
import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

"""
Set up OpenAI API key
"""
f = open("keys/openai_key.txt", "r")
key = f.readlines()[0]
f.close()

os.environ["OPENAI_API_KEY"] = key            # LangChain requires API key in environment

"""
Retrieve vectordb created
"""
search_terms = pd.read_pickle("support/_current_/searchTerms.pkl")

embedding = OpenAIEmbeddings()

persist_directory = 'support/%s/persist' % search_terms

vectordb = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding
    )

print("Processing folder:", search_terms)
print("Size of Vector Database", vectordb._collection.count())    # same as before\

"""
Import a language model (LLM)
"""
llm = ChatOpenAI(model_name="gpt-4", temperature=0)               # gpt model can be changed

"""
Apply language model and vectordb for Chatbot
"""
qa_chain = RetrievalQA.from_chain_type(
    llm,
    ### ----------------------------- PICK 1 OUT OF 3 RELEVANT SPLITS ----------------------------- ###
    # retriever=vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 4, "fetch_k": 6}),
    retriever=vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 4}),
    # retriever=vectordb.as_retriever(),
    ### ------------------------------------------------------------------------------------------- ###
    return_source_documents=True
    )

"""
Ready to use
"""
question = " '''What is the service discussed? Is the sentiment on the service mainly positive or negative? What is a key negative point?''' "  # input question
# question = " '''What is McDonalds?''' " # bad question
template = " If you don't know the answer to the question delimited by triple quotes based on the data given, strictly state 'I don't know'. Keep the answer as concise as possible, with a maximum of three sentences."

prompt = question + template
result = qa_chain({"query": prompt})

print("\n--Results with metadata--")
print(result)
print("\n--The prompt--")
print(result["query"])
print("\n--The sources--")
print(result["source_documents"])
print("\n--The final response--")
print(result["result"])