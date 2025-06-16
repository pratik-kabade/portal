#from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
import time
import timeit
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, load_index_from_storage, StorageContext
from flask import Flask
import os
import logging
import json
from flask import Blueprint, request, jsonify, send_file
from flask_cors import CORS
#from langchain_community.llms import Ollama
from llama_parse import LlamaParse
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
#from  testtojson import text_to_json


os.environ["LLAMA_CLOUD_API_KEY"] = "llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO"
Settings.llm = Ollama(model="llama3") #request_timeout=60.0)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
#llm = Ollama(model="llama3.1:8b")
#llm = Ollama(model="crewai-llama3")
ask_api = Blueprint('askapi', __name__)
@ask_api.route('/ask', methods=['POST'])
def ask():
  """Generate relevant answers """
  query=request.json.get("question",None)
  question = query.strip() if query is not None else ""
  task1 = Task(
          description = question, 
          agent=general_agent,
          tools = [indexSearch1,indexSearch2],
          expected_output = """Answer in english language"""
)
 
  crew = Crew(agents=[general_agent], tasks=[task1], verbose = 2)
  result = crew.kickoff()
  return jsonify({"answer": result}), 200

@tool("Indextool1")
def indexSearch1(): 
  '''Search from  the vectordb present in the persist_dir and answer the query'''
  persist_dir = "/home/genaidevassetv1/Agents/vectordb1"  #actual path
  print("loading existing index")
  storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
  index = load_index_from_storage(storage_context=storage_context)
  return index

@tool("Indextool2")
def indexSearch2(): 
  '''Search from  the vectordb present in the persist_dir and answer the query'''
  persist_dir = "/home/genaidevassetv1/Agents/vectordb2"
  print("loading existing index")
  storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
  index = load_index_from_storage(storage_context=storage_context)
  return index

# Define your general agent
general_agent = Agent(
                role="AI-Assistant",
                goal ="""You are an AI assistant.Your goal is to answer precisely and to the point""",
backstory = """You are an AI assistant that answers questions in a friendly manner.Here are some rules you always follow:
- Generate human readable output, avoid creating output with gibberish text.
- Generate only the requested output, do not include any other language before or after the requested output.
- Never say thank you, that you are happy to help, that you are an AI agent, etc. Just answer directly.
- Never generate offensive or foul language.""",
 # tools = [indexSearch],
  allow_delegation=False,
  verbose=True,
  #llm=Settings.llm,
)

app = Flask(__name__)
CORS(app)
app.register_blueprint(ask_api)



if __name__=='__main__':
    app.run(debug=True, port=5000)

