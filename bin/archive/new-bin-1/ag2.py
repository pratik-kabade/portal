import os
from llama_index.core import (Settings, SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage, ) 
from llama_index.core.tools import QueryEngineTool, ToolMetadata 
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.embeddings import resolve_embed_model
from llama_parse import LlamaParse

os.environ["LLAMA_CLOUD_API_KEY"] = "llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO"
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
Settings.llm = Ollama(model="llama3", request_timeout = 60.0, temperature = 0)

try: 
    storage_context = StorageContext.from_defaults(persist_dir="./Agents/vectordb1") 
    index1 = load_index_from_storage(storage_context) 
    storage_context = StorageContext.from_defaults(persist_dir="./Agents/vectordb2") 
    index2 = load_index_from_storage(storage_context) 
    index_loaded = True 
except:
    index_loaded = False

query_engine1 = index1.as_query_engine()
query_engine2 = index2.as_query_engine()

query_engine_tools = [ 
    QueryEngineTool( 
        query_engine=query_engine1,
        metadata=ToolMetadata(
            name="Ram", 
            description=( "Provides information about Ram " 
                "Use a detailed plain text question as input to the tool."
    ), ), ),
    QueryEngineTool(
        query_engine=query_engine2, 
        metadata=ToolMetadata( 
            name="Shyam",
            description=( "Provides information about Shyam " 
                "Use a detailed plain text question as input to the tool."
    ), ), ),
]

agent = ReActAgent.from_tools( 
    query_engine_tools, 
    verbose=True,
)

response = agent.chat("What are the favorite subjects of Ram and Shyam?")
print(str(response))
