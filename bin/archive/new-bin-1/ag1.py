from llama_index.core.tools import FunctionTool 
from llama_index.core.agent import ReActAgent 
from llama_index.llms.ollama import Ollama 
from llama_index.core import Settings 
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, load_index_from_storage, StorageContext
import nest_asyncio
nest_asyncio.apply()

Settings.llm = Ollama(model="llama3", request_timeout = 60.0, temperature = 0)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

def indexSearch1(query): 
    print("loading existing index of Ram") 
    persist_dir = "./Agents/vectordb1" 
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context=storage_context)
    query_engine = index.as_query_engine()
    result = query_engine.query(query)
    return result

def indexSearch2(query):
    print("loading existing index of Shyam")
    persist_dir = "./Agents/vectordb2"
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context=storage_context)
    query_engine = index.as_query_engine()
    result = query_engine.query(query)
    return result

index_tool1 = FunctionTool.from_defaults(fn=indexSearch1)
index_tool2 = FunctionTool.from_defaults(fn=indexSearch2)

agent= ReActAgent.from_tools([index_tool1,index_tool2], 
    llm = llm, 
    verbose = True 
)

response1 = agent.chat("What are favourite subjects and ages of shyam and ram?")

# response2 = agent.chat("What are the passions of Ram and Shyam?")

# response3 = agent.chat("What are the school names of Ram and Shyam?")

# response4 = agent.chat("What are the ages of Ram and Shyam?")


print('response1:'+str(response1))
# print('response2:'+str(response2))
# print('response3:'+str(response3))
# print('response4:'+str(response4))
