import pandas as pd

def fetchdata(path):
    print('> fetching data..')
    data = pd.read_csv(path)
    dicts = data.to_dict()
    # print(dicts)
    print('===> data fetched')
    return dicts




# from langchain_ollama import OllamaEmbeddings
from llama_index.embeddings.ollama import OllamaEmbedding
embed_model = OllamaEmbedding(model_name="llama3",base_url="http://localhost:11434",)

def creating_embeddings(dicts):
    print('> creating embeddings..')
    embeddings = []
    for key, value in dicts.items():
        key_embedding=embed_model.get_query_embedding(str(key))
        value_embedding=embed_model.get_query_embedding(str(value))
        embeddings.append(
            {
                'key':key, 
                'key_embedding':key_embedding, 
                'value':value,
                'value_embedding':value_embedding
                })
        # print(len(embedding))
    # print(len(embeddings))
    print('==> embeddings created')
    return embeddings




from neo4j import GraphDatabase
# Establish connection to Neo4j
uri = "neo4j://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "genesis"))

def saving_in_graphdb(embeddings, filename):
    print('> saving data in graphdb..')
    
    def store_embeddings(tx, filename, key, key_embedding, value, value_embedding):
        tx.run("""
        CREATE (f:File {name: $filename})
        CREATE (k:Key {name: $key, key_embedding: $key_embedding})
        CREATE (v:Value {name: $value, value_embedding: $value_embedding})
        MERGE (k)-[:KEY_TO_FILE]->(f)
        MERGE (v)-[:VALUE_TO_KEY]->(k)
        """, filename=filename, key=key, key_embedding=key_embedding, value=value, value_embedding=value_embedding)
    
    with driver.session() as session:
        for embedding in embeddings:
            session.execute_write(
                store_embeddings, 
                filename, 
                str(embedding['key']), 
                str(embedding['key_embedding']), 
                str(embedding['value']), 
                str(embedding['value_embedding'])
            )
    
    print('==> data saved in graphdb')




from neo4j import GraphDatabase

# Establish connection to Neo4j
uri = "neo4j://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "genesis"))

def get_relevant_text(prompt, filename):
    print('> fetching relevant text from graphdb..')

    def fetch_data(tx, filename):
        # Fetch all keys and their corresponding values from Neo4j
        result = tx.run("""
        MATCH (f:File {name: $filename})<-[:KEY_TO_FILE]-(k:Key)-[:VALUE_TO_KEY]->(v:Value)
        RETURN k.name AS key, v.name AS value
        """, filename=filename)
        return {record['key']: record['value'] for record in result}
    
    with driver.session() as session:
        stored_data = session.execute_read(fetch_data, filename)
    
    print(f'Stored data: {stored_data}')
    
    # Split the prompt into words or elements
    prompt_elements = prompt.split()
    
    # Find the first matching key in the stored data
    for element in prompt_elements:
        if element in stored_data:
            print(f"Match found: {element}")
            return stored_data[element]
    
    print('==> No relevant text found')
    return None




# Combine the retrieved relevant texts and pass them to the LLM
# combined_text = " ".join(relevant_texts)
from llama_index.llms.ollama import Ollama
llm = Ollama(model="llama3", request_timeout=120.0)

def get_response(prompt):
    print('>>>>> getting response..')
    response = llm.stream_complete(prompt)
    for r in response:
        print(r.delta, end="")