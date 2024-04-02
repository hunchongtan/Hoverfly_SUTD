"""
Remember to install packages before starting!
pip install langchain==0.1.9 chromadb==0.4.24 langchain-openai==0.0.8
"""

import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import shutil
import pandas as pd
from langchain.vectorstores import Chroma

"""
Set up OpenAI API key
"""
f = open("keys/openai_key.txt", "r")
key = f.readlines()[0]
f.close()

os.environ["OPENAI_API_KEY"] = key      # LangChain requires API key in environment

"""
Load Private Documents
"""
loader = TextLoader(file_path="support/_current_/comments.txt", encoding="utf-8")

document = loader.load()

"""
Split Documents into smaller parts
"""
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
splits = text_splitter.split_documents(document)

print("Number of splits in document loaded:", len(splits))

"""
Use OpenAI Embeddings
"""
embedding = OpenAIEmbeddings()

"""
Remove 'persist' directory, if any
"""
search_terms = pd.read_pickle("support/_current_/searchTerms.pkl")
print("Processing folder:", search_terms)

try:
    shutil.rmtree('support/%s/persist' % search_terms)       # remove old version
    print("Deleting previous store")
except:
    print("No store found")

persist_directory = 'support/%s/persist' % search_terms     # create new version

files = os.listdir("support/%s" % search_terms)             # list all files
print("Files in folder:", files)

"""
Apply embeddings on private documents and save in 'persist' directory
"""
vectordb = Chroma.from_documents(
    documents=splits,                           # target the splits created from the documents loaded
    embedding=embedding,                        # use the OpenAI embedding specified
    persist_directory=persist_directory         # store in the persist directory for future use
)

vectordb.persist()                              # store vectordb

print("Persist Directory created.")
print("Size of Vector Database:", vectordb._collection.count())    # same as the number of splits