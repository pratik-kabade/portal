import os
import json
import requests
import sys

# Securely load API key from environment variables
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY", "your-api-key-here")  # Replace with your actual key or set it in env variables
OLLAMA_API_URL = 'http://localhost:11434/api/generate'

class LLM:
    def __init__(self, llm_model, debug_mode=False):
        self.BASE_DIR = 'helpers/data/'
        self.llm_model = llm_model
        self.debug_mode = debug_mode

        if self.debug_mode:
            print('=> LLM Initialized with model:', self.llm_model)

    def fetch_entire_response(self, prompt):
        if self.debug_mode:
            print('>> Fetching entire response for prompt:', prompt)

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

            full_response = ''.join(result)
            if self.debug_mode:
                print(">> Response received:", full_response)

            return full_response

        except requests.exceptions.RequestException as e:
            error_msg = f"Error: {e}"
            if self.debug_mode:
                print(error_msg)
            return error_msg
        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error: {e}"
            if self.debug_mode:
                print(error_msg)
            return error_msg

# Usage example:
if __name__ == "__main__":
    llm_instance = LLM(llm_model='llama2', debug_mode=True)

    if len(sys.argv) > 1:
        inp = sys.argv[1]
    else:
        inp = input("Enter prompt: ")  # Replacing `q` with a proper input mechanism

    response = llm_instance.fetch_entire_response(inp)
    print("LLM Response:", response)


'''
Summary of Fixes:
✅ Fixes get_response method call → Changed to fetch_entire_response
✅ Secure API key handling → Uses os.getenv instead of hardcoding
✅ Fixes undefined q variable → Uses input() for user input
✅ Better debug messages → Prints detailed logs when debug_mode=True
✅ Improved error handling → Logs errors for failed API requests
'''
