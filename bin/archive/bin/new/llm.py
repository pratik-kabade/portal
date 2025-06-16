import os
from llama_index.core import VectorStoreIndex, Settings, load_index_from_storage, StorageContext
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse

# os.environ["LLAMA_CLOUD_API_KEY"] = "llx-Rvjlto0iJiuVlgFAUggwiPM1YGy5wHbnxtdfe8oRNMlArZQu"

class LLM:
    def __init__(self, llm_model, debug_mode=False):
        self.BASE_DIR = 'data/'
        self.llm_model = llm_model
        self.debug_mode = debug_mode

        if self.debug_mode: print('=> LLM Declared')

    def rag_model(self, file_name, prompt):
        if self.debug_mode: print('>> Getting response..')        
        file_path = f"{self.BASE_DIR}{file_name}"
        persist_dir = f"{self.BASE_DIR}vectordb/"

        Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
        Settings.llm = Ollama(model=self.llm_model, request_timeout=30.0, temperature=0)

        documents = LlamaParse(result_type="text").load_data(file_path)

        if not os.path.exists(os.path.join(persist_dir, "default__vector_store.json")):
            print('Creating indexes..')
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=persist_dir)
        else:
            print('Loading indexes..')
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context=storage_context)

        query_engine = index.as_query_engine()
        response = query_engine.query(prompt)
        print(response)

    def get_response(self, prompt):
        if self.debug_mode: print('>> Getting response..')        
        llm = Ollama(model=self.llm_model, request_timeout=30.0, temperature=0)
        response = llm.stream_complete(prompt)
        for r in response:
            print(r.delta, end="")
        print()

# Usage example:
if __name__ == "__main__":
    llm_model = 'llama3'
    llm_instance = LLM(llm_model='llama3')
    llm_instance.rag_model('./data/f1.csv', 'what is first occurence of nanp')
    llm_instance.get_response('Your query prompt')
