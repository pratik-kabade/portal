# ollama_api.py
import requests

def get_llama2_response(prompt):
    url = "http://localhost:11434/api/generate"  # Changed to http
    headers = {"Content-Type": "application/json"}
    data = {"model": "llama2", "prompt": prompt}

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()

    return response.json()["choices"][0]["text"]
