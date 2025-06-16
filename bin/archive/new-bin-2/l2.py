from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
import time
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, load_index_from_storage, StorageContext
import os
from llama_index.core.tools import QueryEngineTool
from llama_parse import LlamaParse

os.environ["LLAMA_CLOUD_API_KEY"] = "llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO"

Settings.llm = Ollama(model="llama3", request_timeout=60.0, temperature = 0)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
persist_dir="./Agents/vectordb2"
print("Start 2")

if not os.path.exists(os.path.join(persist_dir, "default__vector_store.json")):
    print("creating new index 2")
    filepath = './Shyam.pdf'
    documents = LlamaParse(result_type="text").load_data(filepath)
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=persist_dir)
else:
    print("loading existing index 2")
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context=storage_context)

query_engine = index.as_query_engine()

print("2", query_engine)

tool2 = QueryEngineTool.from_defaults( query_engine, 
    name="Shyam", 
    description="A RAG engine describing Shyam",
)

print("3", tool2)





