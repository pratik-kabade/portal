import os
import time
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, load_index_from_storage, StorageContext
from llama_index.core.tools import QueryEngineTool
from llama_parse import LlamaParse
from llama_index.core.agent import ReActAgent 
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings 
import nest_asyncio 
nest_asyncio.apply()

os.environ["LLAMA_CLOUD_API_KEY"] = "llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO"

Settings.llm = Ollama(model="llama3", request_timeout=60.0, temperature = 0)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

base_persist_dir = "./Agents/vectordb"
filepaths = ['./data/Ram.pdf', './data/Shyam.pdf']

for i in range(len(filepaths)):
    filepath = filepaths[i]
    item=i+1
    persist_dir = base_persist_dir+str(item)
    if not os.path.exists(os.path.join(persist_dir, "default__vector_store.json")):
        print("creating new index " + str(item))
        documents = LlamaParse(result_type="text").load_data(filepath)
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=persist_dir)
    else:
        print("loading existing index " + str(item))
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context=storage_context)

print('done')