import os
import argparse
import time
import json
from prompts import myprompts
from prompts import genesis_prompts

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama


import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


from llama_parse import LlamaParse
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO"

file_path = "/home/genaidevassetv2/llama_index/data/Aruba-Instant-8.12.0.0-User-Guide.pdf"
documents = LlamaParse(result_type="text").load_data(file_path)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

Settings.llm = Ollama(model="llama3", request_timeout=30.0, temperature=0)
index = VectorStoreIndex.from_documents(
    documents)


query_engine = index.as_query_engine()

parser = argparse.ArgumentParser()
parser.add_argument('input',
                        type=str,
                        help='Enter the query to pass into the LLM')
args = parser.parse_args()
userstory = args.input

mainPrompt = "[INST]\n" + myprompts.TC_PERSONA + "\n\n" + myprompts.TC_FORMAT + "\n[/INST]\n" + "<<<USERSTORY>>>\n" + userstory


response = query_engine.query(mainPrompt)
print(response)

