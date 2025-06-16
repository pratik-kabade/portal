from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOllama
 
memory = ConversationBufferMemory()


Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")





llm = ChatOllama(
    model="llama3",
    temperature=0,
)
 
# index = SimpleVectorIndex.load_from_disk("/home/genaidevassetv1/dev/vectorstore/Bug-Triage")
documents = SimpleDirectoryReader("/home/genaidevassetv1/dev/data/Bug-Triage").load_data()
index = VectorStoreIndex.from_documents(documents)

conversation_chain = ConversationalRetrievalChain(
    llm=llm,
    retriever=index.as_retriever(),
    memory=ConversationBufferMemory()
)

response = conversation_chain({"question": "Can you tell me about the last document I uploaded?"})
print(response)


 
