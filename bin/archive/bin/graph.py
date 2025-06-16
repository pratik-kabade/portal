from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

# Step 1: Extract Data from Neo4j
def get_all_nodes(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    query = "MATCH (n) RETURN n"
    
    with driver.session() as session:
        result = session.run(query)
        nodes = [record["n"] for record in result]
    
    driver.close()
    return nodes

def get_all_relationships(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    query = "MATCH ()-[r]->() RETURN r"
    
    with driver.session() as session:
        result = session.run(query)
        relationships = [record["r"] for record in result]
    
    driver.close()
    return relationships

uri = "bolt://localhost:7687"
user = "neo4j"
password = "genesis"

nodes = get_all_nodes(uri, user, password)
# print(nodes)
relationships = get_all_relationships(uri, user, password)
# print(relationships)







# Step 2: Convert Data to Embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Convert nodes to embeddings
node_embeddings = {}
for node in nodes:
    properties = dict(node)
    text = " ".join([f"{key}: {value}" for key, value in properties.items()])
    embedding = model.encode(text)
    node_embeddings[node.element_id] = embedding
print(node_embeddings)

# Convert relationships to embeddings
relationship_embeddings = {}
for relationship in relationships:
    properties = dict(relationship)
    text = " ".join([f"{key}: {value}" for key, value in properties.items()])
    embedding = model.encode(text)
    relationship_embeddings[relationship.id] = embedding
# print(relationship_embeddings)






# Step 3: Feed Embeddings to the LLM
# def feed_embeddings_to_llm(embeddings):
#     # Your logic to feed embeddings to the LLM
#     print(embeddings)
#     pass

import requests
import json

def feed_embeddings_to_llm(node_embeddings, relationship_embeddings):
    url = "https://localhost:11434/v1/train"  # Assuming this is the training endpoint for Ollama Llama2

    # Combine node and relationship embeddings
    embeddings = {
        "nodes": node_embeddings,
        "relationships": relationship_embeddings
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(embeddings), verify=False)

    if response.status_code == 200:
        print("Embeddings successfully sent to the LLM for training.")
    else:
        print(f"Failed to send embeddings. Status code: {response.status_code}, Response: {response.text}")

# Example usage
# feed_embeddings_to_llm(node_embeddings, relationship_embeddings)











# Step 4:
import os
import argparse
import time
import json
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
import logging
import sys
from llama_parse import LlamaParse
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO"

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

csv_file_path = node_embeddings

file_path = csv_file_path
documents = LlamaParse(result_type="text").load_data(file_path)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

Settings.llm = Ollama(model="llama3", request_timeout=30.0, temperature=0)
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()

response = query_engine.query("what is the firstoccurence of NANP?")
print(response)
