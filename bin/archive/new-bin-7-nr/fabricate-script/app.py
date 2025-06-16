from llama_index.llms.ollama import Ollama
import pandas as pd
import os
from templates import PROMPT_HEADER, PROMPT_FOOTER

os.environ["NO_PROXY"] = '127.0.0.1, localhost'

def run_llm(prompt):
    print('Running LLM for:', prompt)
    try:
        llm = Ollama(model='llama2', request_timeout=300.0, temperature=0)
        final_prompt = f'{PROMPT_HEADER} {prompt} {PROMPT_FOOTER}'
        response = llm.stream_complete(final_prompt)

        last_line = ''
        for r in response:
            last_line = str(r)

        return last_line
    except Exception as e:
        print(f"Error in LLM response for prompt '{prompt}':", e)
        return "Error in generating response"

data = pd.read_csv('data.csv')

for index, row in data.iterrows():
    original_name = row['name']
    llm_resp = run_llm(original_name)

    filename = f'data/{index}.py'
    with open(filename, mode='w') as script_file:
        script_file.write(llm_resp)

print("Process complete. LLM responses saved to text files.")
