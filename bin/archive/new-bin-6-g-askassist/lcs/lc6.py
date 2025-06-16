initial_db = False
DATA_PATH = "test/data/"
OLLAMA_MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434"
CHROMA_PATH = "chroma/"

## langchain split config
# md headers
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
    ("####", "Header 4"),
]

# chunk sizes
chunk_size = 500
chunk_overlap = 100


# from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import TextLoader
import os

documents = []

for file in os.listdir(DATA_PATH):
    loader = TextLoader(DATA_PATH + file)
    documents.append(loader.load()[0])


documents[0].metadata
len(documents[0].page_content)




from langchain.text_splitter import MarkdownHeaderTextSplitter

text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
chunks_array= []
for doc in documents:
    chunks_array.append(text_splitter.split_text(doc.page_content))
    # append source metadata to each chunk
    for chunk in chunks_array[-1]:
        # combine metadate
        chunk.metadata = doc.metadata
len(chunks_array)


# Char-level splits
from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len, add_start_index=True
)
chunks_array_txt_base = []
counter = 0
for document in chunks_array:
    for chunk in document:
        splits = text_splitter.split_documents([chunk])
        chunks_array_txt_base.append(splits)
        counter += 1
        
all_document_chunks = [chunk for document in chunks_array_txt_base for chunk in document]





# TEST OLLAMA CONNECTION ##
from langchain_community.llms import Ollama
llm = Ollama(base_url=OLLAMA_URL, model=OLLAMA_MODEL)
print(llm.invoke("Who is Alice?"))



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
query = "Who is Alice?"
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
