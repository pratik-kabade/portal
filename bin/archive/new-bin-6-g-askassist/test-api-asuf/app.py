from llm import LlamaIndexManager

PROJECT = 'RDKB' 
FILE = 'data/test/asuf.txt'
QN = 'what is this document about?'


instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
queryengine = instance.getChatEngine(PROJECT)
response = queryengine.chat(QN)


# llama_index_manager = LlamaIndexManager.clsLlamaIndexManager.get_instance()
# llama_index_manager.run_ingest(FILE, PROJECT)
# a = llama_index_manager.getQueryEngine(PROJECT)



print(response)


# curl -X POST -H "Content-Type: application/json" -d '{"question" : "hi", "project_name" : "RDKB"}' http://localhost:5000/api/ask
