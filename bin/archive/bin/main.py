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
Settings.llm = Ollama(model="llama2", request_timeout=30.0, temperature=0)

documents = LlamaParse(result_type="text").load_data(file_path)






# =================> db-json
if not os.path.exists(os.path.join(persist_dir, "default__vector_store.json")):
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=persist_dir)
else:
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context=storage_context)

query_engine = index.as_query_engine()
response = query_engine.query("Give me all the data of NANP from the alarms data")
print(response)





# # =================> noe4j
# from llama_index.core import KnowledgeGraphIndex
# from llama_index.graph_stores.neo4j import Neo4jGraphStore

# username = "neo4j"
# password = "genesis"
# url = "bolt://127.0.0.1:7687"
# database = "neo4j"

# print('starting with db')

# graph_store = Neo4jGraphStore(
#     username=username,
#     password=password,
#     url=url,
#     database=database,
# )

# storage_context = StorageContext.from_defaults(graph_store=graph_store)

# documents = SimpleDirectoryReader(
#     BASE_DIR
# ).load_data()


# # NOTE: can take a while!
# index = KnowledgeGraphIndex.from_documents(
#     documents,
#     storage_context=storage_context,
#     max_triplets_per_chunk=2,
# )

# query_engine = index.as_query_engine(
#     include_text=False, response_mode="tree_summarize"
# )

# response = query_engine.query("Tell me more about Interleaf")

# print(response)