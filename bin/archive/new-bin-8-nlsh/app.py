import os
from llama_index.core import VectorStoreIndex, Settings, load_index_from_storage, StorageContext
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
import json
import requests
import sys

os.environ["LLAMA_CLOUD_API_KEY"] = "llx-Rvjlto0iJiuVlgFAUggwiPM1YGy5wHbnxtdfe8oRNMlArZQu"
OLLAMA_API_URL = 'http://localhost:11434/api/generate'

class LLM:
    def __init__(self, llm_model, debug_mode=False):
        self.BASE_DIR = 'bin/data/'
        self.llm_model = llm_model
        self.debug_mode = debug_mode

        if self.debug_mode: print('=> LLM Declared')

    def rag_model(self, file_name, prompt):
        if self.debug_mode: print('>> Getting response from documents..')
        file_path = f"{self.BASE_DIR}{file_name}"
        persist_dir = f"{self.BASE_DIR}vectordb/{str(file_name).replace('/', '-')}"

        Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
        Settings.llm = Ollama(model=self.llm_model, request_timeout=90.0, temperature=0)

        if os.path.exists(file_path):
            documents = LlamaParse(result_type="text").load_data(file_path)
        else:
            return 'no such file found'

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
        # print(response)
        return str(response)

    def get_response(self, prompt):
        if self.debug_mode: print('>> Getting llm response..')
        llm = Ollama(model=self.llm_model, request_timeout=30.0, temperature=0)
        response = llm.stream_complete(prompt)
        for r in response:
            print(r.delta, end="")
        print()


    def _stream_response(self, prompt):
        """[BASIC] Streams the model's response token by token."""
        if self.debug_mode: print('>> Streaming response..')
        headers = {'Content-Type': 'application/json'}
        data = {'model': self.llm_model, 'prompt': prompt}

        try:
            with requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data), stream=True) as response:
                response.raise_for_status()

                # Stream each token back to the client
                for line in response.iter_lines():
                    if line:
                        json_res = json.loads(line.decode('utf-8'))
                        if 'response' in json_res:
                            yield json_res['response'] + '\n'

        except requests.exceptions.RequestException as e:
            yield f"Error: {e}\n"
        except json.JSONDecodeError as e:
            yield f"JSON decode error: {e}\n"

    def fetch_entire_response(self, prompt):
        """[BASIC] Fetches the entire model response at once."""
        if self.debug_mode: print('>> Fetching entire response..')
        headers = {'Content-Type': 'application/json'}
        data = {'model': self.llm_model, 'prompt': prompt}

        try:
            response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data))
            response.raise_for_status()

            # Collect the entire response
            result = []
            for line in response.iter_lines():
                if line:
                    json_res = json.loads(line.decode('utf-8'))
                    if 'response' in json_res:
                        result.append(json_res['response'])
            
            # Return the joined result
            return ''.join(result)

        except requests.exceptions.RequestException as e:
            return f"Error: {e}"
        except json.JSONDecodeError as e:
            return f"JSON decode error: {e}"



# Usage example:
if __name__ == "__main__":
    llm_model = 'llama2'
    llm_instance = LLM(llm_model=llm_model, debug_mode=True)

    if len(sys.argv) > 1:
        inp = sys.argv[1]
        resp = llm_instance.rag_model('PRIN.pdf', inp)
    else:
        resp = llm_instance.rag_model('PRIN.pdf', 'what is this document about?')
    
    print(resp)



    # print(llm_instance.stream_response('hi'))
    # print(llm_instance.fetch_entire_response('hi'))