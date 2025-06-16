from llama_index.core import SimpleDirectoryReader
from llama_index.core.indices.list import ListIndex
from llama_index.llms.ollama import Ollama
from llama_index.core import ServiceContext
 
documents = SimpleDirectoryReader('pdf').load_data()
 
llm = Ollama(model="llama3")  # You can also use mistral, gemma, etc.
 
service_context = ServiceContext.from_defaults(llm=llm)
 
index = ListIndex.from_documents(documents, service_context=service_context)
query_engine = index.as_query_engine()
response = query_engine.query("What is the main topic of the document?")
print(response)