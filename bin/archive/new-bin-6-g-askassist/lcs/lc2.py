from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3",
    temperature=0,
    # other params...
)



from langchain_core.messages import AIMessage

messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate every sentence i give you from now on.",
    )
]
ai_msg = llm.invoke(messages)
print(1, ai_msg.content)

messages = [
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
print(2, ai_msg.content)

messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate every sentence i give you from now on.",
    ),
    ("human", "I love programming."),
    ("human", "I want to code in python"),
]
ai_msg = llm.invoke(messages)
print(3, ai_msg.content)
