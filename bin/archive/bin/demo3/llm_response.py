from llama_index.llms.ollama import Ollama

def get_response(model, prompt):
    llm = Ollama(model = model, request_timeout=120.0)
    print('>>>>> Getting response..')
    response = llm.stream_complete(prompt)
    for r in response:
        print(r.delta, end="")
    print()