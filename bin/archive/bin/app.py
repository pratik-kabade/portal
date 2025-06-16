import os
import argparse
import time
import json
import pandas as pd
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, load_index_from_storage, StorageContext
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
import logging
import sys
from llama_parse import LlamaParse
from neo4j import GraphDatabase

os.environ["LLAMA_CLOUD_API_KEY"] = "llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO"

BASE_DIR = '/home/genaidevassetv1/portal/data/'
file_path = f"{BASE_DIR}Alarms.csv"
persist_dir = f"{BASE_DIR}vectordb/"

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
Settings.llm = Ollama(model="llama3", request_timeout=30.0, temperature=0)

documents = LlamaParse(result_type="text").load_data(file_path)

if not os.path.exists(os.path.join(persist_dir, "default__vector_store.json")):
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=persist_dir)
else:
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context=storage_context)

query_engine = index.as_query_engine()
response = query_engine.query("what is the first occurrence of NANP?")
print(response)



from neo4j import GraphDatabase

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "genesis"

# Function to create a Neo4j driver
def create_driver(uri, user, password):
    return GraphDatabase.driver(uri, auth=(user, password))

# Function to store embeddings in Neo4j
def store_embeddings_in_neo4j(driver, embeddings):
    with driver.session() as session:
        for doc_id, embedding in embeddings.items():
            session.run(
                "MERGE (d:Document {id: $id}) "
                "SET d.embedding = $embedding",
                id=doc_id, embedding=embedding
            )

# Assuming you have a method to extract embeddings from your index
embeddings = index.get_embeddings()  # Replace with the correct method to get embeddings

# Create Neo4j driver and store embeddings
driver = create_driver(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
store_embeddings_in_neo4j(driver, embeddings)

print("Embeddings stored in Neo4j successfully.")
