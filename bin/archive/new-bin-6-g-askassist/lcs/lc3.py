import json

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# json_schema = {
#     "title": "Person",
#     "description": "Identifying information about a person.",
#     "type": "object",
#     "properties": {
#         "name": {"title": "Name", "description": "The person's name", "type": "string"},
#         "age": {"title": "Age", "description": "The person's age", "type": "integer"},
#         "fav_food": {
#             "title": "Fav Food",
#             "description": "The person's favorite food",
#             "type": "string",
#         },
#     },
#     "required": ["name", "age"],
# }


# messages = [
#     HumanMessage(
#         content="Please tell me about a person using the following JSON schema:"
#     ),
#     HumanMessage(content="{dumps}"),
#     HumanMessage(
#         content="Now, considering the schema, tell me about a person named John who is 35 years old and loves pizza."
#     ),
# ]

# prompt = ChatPromptTemplate.from_messages(messages)
# dumps = json.dumps(json_schema, indent=2)

# chain = prompt | llm | StrOutputParser()

# print(1, chain.invoke({"dumps": dumps}))








llm = ChatOllama(model="llama3")

# messages = [
#     HumanMessage(
#         content="Please tell me about a person who is skilled in dotnet"
#     ),
#     HumanMessage(
#         content="which languages are they familiar with?"
#     ),
# ]

messages_arr = [
    "who is frank underwood",
    "which tv show is he from?",
    "who is his wife?",
]

messages_cont = [HumanMessage(content=i) for i in messages_arr]

# messages = [
#     HumanMessage(
#         content="who is frank underwood"
#     ),
#     HumanMessage(
#         content="which tv show is he from?"
#     ),
#     HumanMessage(
#         content="who is his wife?"
#     ),
#     HumanMessage(
#         content="whats her age?"
#     ),
# ]

prompt = ChatPromptTemplate.from_messages(messages_cont)

chain = prompt | llm | StrOutputParser()

print(chain.invoke({}))

