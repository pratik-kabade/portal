import time
import nest_asyncio
import os
from llama_index.core import VectorStoreIndex, Settings, load_index_from_storage, StorageContext, download_loader
from llama_index.readers.wikipedia import WikipediaReader
from llama_index.llms.ollama import Ollama
from llama_index.core.embeddings import resolve_embed_model

nest_asyncio.apply()
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-Rvjlto0iJiuVlgFAUggwiPM1YGy5wHbnxtdfe8oRNMlArZQu"
loader = WikipediaReader()
documents = loader.load_data(
    pages=[
        "Berlin",
        "Santiago",
        "Moscow",
        "Tokyo",
        "Jakarta",
        "Cairo",
        "Bogota",
        "Shanghai",
        "Damascus",
    ]
)

Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
Settings.llm = Ollama(model='llama3', request_timeout=30.0, temperature=0)

index = VectorStoreIndex(documents, use_async=True)

query_engine = index.as_query_engine()
res = query_engine.query("What is the etymology of Jakarta?")
print(res)
