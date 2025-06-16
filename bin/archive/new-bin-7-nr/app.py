from llama_index.llms.ollama import Ollama
import pandas as pd
from templates import prompt_template

def run_llm(prompt):
    print('Running LLM for:', prompt)
    try:
        llm = Ollama(model='llama2', request_timeout=300.0, temperature=0)
        final_prompt = prompt_template + prompt
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
