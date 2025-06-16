initial_db = True
DATA_PATH = "rdk_new_docs/"
OLLAMA_MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434"
CHROMA_PATH = "chroma/"

# chunk sizes
chunk_size = 500
chunk_overlap = 100

from langchain.document_loaders import PyPDFLoader
import os

documents = []

for file in os.listdir(DATA_PATH):
    if file.endswith(".pdf"):  # Make sure you're loading PDF files
        loader = PyPDFLoader(DATA_PATH + file)
        documents.extend(loader.load())

documents[0].metadata
len(documents[0].page_content)

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len, add_start_index=True
)

chunks_array = []
for doc in documents:
    chunks = text_splitter.split_text(doc.page_content)
    doc_chunks = []
    for chunk in chunks:
        chunk_with_metadata = {
            "page_content": chunk,
            "metadata": doc.metadata
        }
        doc_chunks.append(chunk_with_metadata)
    chunks_array.append(doc_chunks)

from langchain.schema import Document

all_document_chunks = [
    Document(page_content=chunk["page_content"], metadata=chunk["metadata"])
    for document in chunks_array for chunk in document
]






q='what is description of RBUS is not notifying publishing event'
# TEST OLLAMA CONNECTION ##
from langchain_community.llms import Ollama
llm = Ollama(base_url=OLLAMA_URL, model=OLLAMA_MODEL)
print(llm.invoke(q))



__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma

# create chroma db or load db from disk
if initial_db:
    chroma_db = Chroma.from_documents(all_document_chunks, OllamaEmbeddings(base_url=OLLAMA_URL, model=OLLAMA_MODEL), persist_directory=CHROMA_PATH)

## load chroma db from disk

chroma_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=OllamaEmbeddings(base_url=OLLAMA_URL, model=OLLAMA_MODEL))



# test similarity search
query = q
result_chunks = chroma_db.similarity_search(query)

chroma_knowledge = ""
for id, chunk in enumerate(result_chunks):
    source_id = id + 1
    chroma_knowledge += "[" + str(source_id) +"] \n" + chunk.page_content + "\n"

sources = ""
for id, chunk in enumerate(result_chunks):
    source_id = id + 1
    sources += "[" + str(source_id) + "] \n" + chunk.metadata["source"] + "\n"


prompt = "Answer the following question using the provided knowledge:\n\n###KNOWLEDGE: " + chroma_knowledge + '\n\n###QUESTION: ' + query
result = "\n\n\n\nRAG Answer:\n" + llm.invoke(prompt) + "\n\nReferences:\n" + sources 
print(result)
