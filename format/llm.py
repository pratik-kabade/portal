import ollama

def read_img(img_path, prompt):
    i = [img_path]

    client = ollama.Client(host='http://localhost:11434/')
    response = ollama.chat(model='qwen2.5vl:32b', messages=[{'role':'user', 'content': prompt, 'images':i}])
    text = response['message']['content']
    print(text)
    return text
