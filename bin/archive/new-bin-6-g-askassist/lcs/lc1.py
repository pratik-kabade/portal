from langchain_community.llms import Ollama
llm = Ollama(model="llama3")
a = llm.invoke("Tell me a joke")
print(a)

