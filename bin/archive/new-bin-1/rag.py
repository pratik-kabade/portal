import time
import nest_asyncio
import os
from llama_index.core import VectorStoreIndex, Settings, load_index_from_storage, StorageContext, download_loader
from llama_index.llms.ollama import Ollama
from llama_index.core.embeddings import resolve_embed_model
from llama_parse import LlamaParse

# nest_asyncio.apply()
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-Rvjlto0iJiuVlgFAUggwiPM1YGy5wHbnxtdfe8oRNMlArZQu"

# Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
# Settings.llm = Ollama(model='llama3', request_timeout=30.0, temperature=0)

# documents = os.listdir('db')
# index = VectorStoreIndex(documents, use_async=True)

# query_engine = index.as_query_engine()
# res = query_engine.query("What is the etymology of Jakarta?")
# print(res)



# Set base directory and vector storage path
base_dir = "db/"  # Change this to your actual base directory
persist_dir = os.path.join(base_dir, "vectordb/")

# Set up embedding model and LLM
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
Settings.llm = Ollama(model="llama3", request_timeout=30.0, temperature=0)

# Function to process each file in the directory
def process_files_in_folder(folder_path):
    all_documents = []

    # Iterate through all files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        # Check if the file path is a file, not a subdirectory
        if os.path.isfile(file_path):
            print(f"Processing file: {file_name}")
            documents = LlamaParse(result_type="text").load_data(file_path)
            all_documents.extend(documents)

    # Check if the index already exists; otherwise, create a new one
    if not os.path.exists(os.path.join(persist_dir, "default__vector_store.json")):
        print('Creating indexes...')
        index = VectorStoreIndex.from_documents(all_documents)
        index.storage_context.persist(persist_dir=persist_dir)
    else:
        print('Loading indexes...')
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context=storage_context)

    return index

# Define folder path and prompt
folder_path = base_dir  # Change this to your actual folder path
prompt = "what is status of rdkb-273"  # Set your query prompt

# Process files and query the index
index = process_files_in_folder(folder_path)
query_engine = index.as_query_engine()
response = query_engine.query(prompt)
print(response)
