# from langchain.chains import LLMChain
# from langchain.memory import ConversationBufferMemory
# from langchain_experimental.chat_models import Llama2Chat


# from langchain_core.messages import SystemMessage
# from langchain_core.prompts.chat import (
#     ChatPromptTemplate,
#     HumanMessagePromptTemplate,
#     MessagesPlaceholder,
# )

# template_messages = [
#     SystemMessage(content="You are a helpful assistant."),
#     MessagesPlaceholder(variable_name="chat_history"),
#     HumanMessagePromptTemplate.from_template("{text}"),
# ]
# prompt_template = ChatPromptTemplate.from_messages(template_messages)

# from langchain_community.llms import HuggingFaceTextGenInference

# llm = HuggingFaceTextGenInference(
#     inference_server_url="http://localhost:11434/",
#     max_new_tokens=512,
#     top_k=50,
#     temperature=0.1,
#     repetition_penalty=1.03,
# )

# model = Llama2Chat(llm=llm)


# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# chain = LLMChain(llm=model, prompt=prompt_template, memory=memory)


# print(
#     chain.run(
#         text="What can I see in Vienna? Propose a few locations. Names only, no details."
#     )
# )



# print(chain.run(text="Tell me more about #2."))






# from langchain_community.llms import Ollama
# llm = Ollama(model="llama3")
# a = llm.invoke("Tell me a joke")
# print(a)









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
print(ai_msg.content)

messages = [
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
print(ai_msg.content)




# from langchain_core.prompts import ChatPromptTemplate

# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a helpful assistant that translates {input_language} to {output_language}.",
#         ),
#         ("human", "{input}"),
#     ]
# )

# chain = prompt | llm
# chain.invoke(
#     {
#         "input_language": "English",
#         "output_language": "German",
#         "input": "I love programming.",
#     }
# )