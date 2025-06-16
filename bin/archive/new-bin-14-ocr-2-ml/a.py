import ollama
client = ollama.Client(host='http://localhost:11434/')


def read_img(q, i):
    response = ollama.chat(model='gemma3:12b', messages=[{'role':'user', 'content': q, 'images':i}])
    return response['message']['content']



prompt = '''
just give me the list of all ports present in the image
'''
img_path = ['images/img.JPG']


print(read_img(prompt, img_path))
