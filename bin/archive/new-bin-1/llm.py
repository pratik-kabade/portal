import os
import nest_asyncio
import asyncio
from concurrent.futures import ThreadPoolExecutor
from llama_index.core import VectorStoreIndex, Settings, load_index_from_storage, StorageContext
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

os.environ["LLAMA_CLOUD_API_KEY"] = "llx-Rvjlto0iJiuVlgFAUggwiPM1YGy5wHbnxtdfe8oRNMlArZQu"

class LLM:
    def __init__(self, llm_model):
        self.BASE_DIR = 'data/'
        self.llm_model = llm_model
        self.executor = ThreadPoolExecutor() 
        
    async def rag_model(self, file_name, prompt):
        file_path = f"{self.BASE_DIR}{file_name}"
        persist_dir = f"{self.BASE_DIR}vectordb/"

        Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
        Settings.llm = Ollama(model=self.llm_model, request_timeout=30.0, temperature=0)

        # Since LlamaParse might have async parts, we handle it in an executor.
        documents = await asyncio.get_running_loop().run_in_executor(
            self.executor, lambda: LlamaParse(result_type="text").load_data(file_path)
        )

        if not os.path.exists(os.path.join(persist_dir, "default__vector_store.json")):
            print('Creating indexes..')
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=persist_dir)
        else:
            print('Loading indexes..')
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context=storage_context)

        query_engine = index.as_query_engine()
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(self.executor, query_engine.query, prompt)  # Running in a thread
        print(response)

    async def get_response(self, prompt):
        llm = Ollama(model=self.llm_model, request_timeout=30.0, temperature=0)
        response = llm.stream_complete(prompt)

        # Handle the synchronous generator in a separate thread
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self.executor, self._handle_stream_response, response)

    def _handle_stream_response(self, response):
        # Handling the synchronous generator output
        for r in response:
            print(r.delta, end="")
        print()

    async def handle_requests(self, tasks):
        await asyncio.gather(*tasks)  # Run all tasks concurrently

# Usage example:
if __name__ == "__main__":
    llm_model = 'llama3'
    llm_instance = LLM(llm_model=llm_model)

    # Creating async tasks
    tasks = [
        llm_instance.get_response('hi'),
        llm_instance.rag_model('f1.csv', 'what is first occurrence of nanp'),
        llm_instance.get_response('what is 2x3'),
        llm_instance.get_response('who are you'),
    ]

    # Running the tasks concurrently
    asyncio.run(llm_instance.handle_requests(tasks))
