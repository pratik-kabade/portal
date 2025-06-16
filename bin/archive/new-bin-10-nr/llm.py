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

    def fetch_entire_response(self, prompt):
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



import re

def extract_number(response):
    match = re.search(r'\b\d+\b', response)
    return int(match.group()) if match else None

# Usage example:
if __name__ == "__main__":


    new_tcs = 'replay captured alarms, set the filter condition, Free -m, replay captured alarms'


    def generate_cases(new_tcs):
        # from functions.llm import LLM
        # from functions.utils import get_llm_base_scripts, extract_number

        llm_instance = LLM(llm_model='llama2', debug_mode=False)
        from app import get_llm_base_scripts

        final_dict = get_llm_base_scripts()['entire_dict']
        q_names = get_llm_base_scripts()['names']

        single_tcs = new_tcs.split(',')

        seq = []

        for single_tc in single_tcs:
            q = f"""
        Given the following dictionary:
        {q_names}
        I want to find the key corresponding to the value that best matches the input: "{single_tc}". 

        Respond in the format: "key:#" where "#" is the single key number. Do not include any other text or explanation.
        """    
            resp = llm_instance.fetch_entire_response(q)
            ans = extract_number(resp)
            seq.append(ans)

        final_file = ''
        index = 0
        for index in range(len(seq)):
            # print(1, seq[index], 2, final_dict[seq[index]])
            final_file += f'STEP: {index}\n'
            final_file += final_dict[seq[index]]['content']

        with open('file.txt', 'w') as file:
            file.write(final_file)
        print('file saved!')


    generate_cases(new_tcs)

    # if len(sys.argv) > 1:
    #     inp = sys.argv[1]
    #     resp = llm_instance.get_response(inp)
    # else:
    #     resp = llm_instance.get_response(q)
