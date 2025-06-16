import os
import json
import requests
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv
from gevent.pywsgi import WSGIServer
from gevent import monkey

# Apply monkey patching to make standard library I/O operations asynchronous
monkey.patch_all()

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Fetch Ollama API URL from environment variables
OLLAMA_API_URL = os.getenv("LLM_GENERATE_URL")

def stream_response(prompt):
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'llama3',
        'prompt': prompt
    }
    try:
        with requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data), stream=True) as response:
            response.raise_for_status()
            
            # Process the streaming response
            for line in response.iter_lines():
                if line:
                    json_res = json.loads(line.decode('utf-8'))
                    if 'response' in json_res:
                        yield json_res['response']

            yield '\n'

    except requests.exceptions.RequestException as e:
        return f"Error: {e}\n"
    except json.JSONDecodeError as e:
        return f"JSON decode error: {e}\n"


# Rout
@app.route('/')
def home():
    return jsonify({"message": "Server is running"}), 200

@app.route('/get-response', methods=['POST'])
def get_response():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    # Handle the request asynchronously
    response = stream_response(prompt)
    return Response(response, content_type='text/plain')

if __name__ == "__main__":
    # Run the server with gevent WSGIServer to handle multiple requests simultaneously
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    print("Server is running on http://127.0.0.1:5000")
    http_server.serve_forever()

# Use the following command to test:
# curl -X POST http://127.0.0.1:5000/get-response -H "Content-Type: application/json" -d '{"prompt": "generate 10paragraph speech on microsoft"}'
# curl -X POST http://127.0.0.1:5000/get-response -H "Content-Type: application/json" -d '{"prompt": "generate 10paragraph speech on google"}'
