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

def saving_in_graphdb(embeddings):
    print('> saving data in graphdb..')
    
    def store_embeddings(tx, key, key_embedding, value, value_embedding):
        tx.run("""
        CREATE (n:TextNode {
            key: $key, 
            key_embedding: $key_embedding, 
            value: $value, 
            value_embedding: $value_embedding
        })
        """, key=key, key_embedding=key_embedding, value=value, value_embedding=value_embedding)
    
    with driver.session() as session:
        for embedding in embeddings:
            session.execute_write(
                store_embeddings, 
                str(embedding['key']), 
                str(embedding['key_embedding']), 
                str(embedding['value']), 
                str(embedding['value_embedding'])
            )
    
    print('==> data saved in graphdb')





# def get_relevant_data(tx, query_embedding):
#     result = tx.run(
#         """
#         MATCH (n:TextNode)
#         WITH n, 
#              reduce(s = 0.0, i in range(0, size(n.key_embedding)-1) | s + n.key_embedding[i] * $query_embedding[i]) AS key_dot_product,
#              reduce(s1 = 0.0, i in range(0, size(n.key_embedding)-1) | s1 + n.key_embedding[i] * n.key_embedding[i]) AS key_norm1,
#              reduce(s2 = 0.0, i in range(0, size($query_embedding)-1) | s2 + $query_embedding[i] * $query_embedding[i]) AS key_norm2,
             
#              reduce(s3 = 0.0, i in range(0, size(n.value_embedding)-1) | s3 + n.value_embedding[i] * $query_embedding[i]) AS value_dot_product,
#              reduce(s4 = 0.0, i in range(0, size(n.value_embedding)-1) | s4 + n.value_embedding[i] * n.value_embedding[i]) AS value_norm1,
#              reduce(s5 = 0.0, i in range(0, size($query_embedding)-1) | s5 + $query_embedding[i] * $query_embedding[i]) AS value_norm2
             
#         RETURN n.key AS key, 
#                n.value AS value, 
#                (key_dot_product / (sqrt(key_norm1) * sqrt(key_norm2))) AS key_similarity,
#                (value_dot_product / (sqrt(value_norm1) * sqrt(value_norm2))) AS value_similarity
#         ORDER BY key_similarity DESC, value_similarity DESC LIMIT 5
#         """, query_embedding=query_embedding)
    
#     return [(record["key"], record["value"], record["key_similarity"], record["value_similarity"]) for record in result]

# def retrive_data(query_text):
#     print('> retrieving data..')
#     query_embedding = embed_model.get_query_embedding(query_text)
    
#     with driver.session() as session:
#         relevant_data = session.execute_read(get_relevant_data, query_embedding)
    
#     # print(relevant_data)
#     print('==> data retrieved')
#     return relevant_data

import numpy as np

def get_relevant_text(prompt):
    print('> fetching relevant text from graphdb..')

    # Generate embedding for the prompt
    prompt_embedding = embed_model.get_query_embedding(prompt)
    
    def fetch_embeddings(tx):
        # Fetch all embeddings and their associated keys and values from Neo4j
        result = tx.run("MATCH (n:TextNode) RETURN n.key AS key, n.key_embedding AS key_embedding, n.value AS value, n.value_embedding AS value_embedding")
        return [
            {
                'key': record['key'],
                'key_embedding': np.fromstring(record['key_embedding'][1:-1], sep=','),
                'value': record['value'],
                'value_embedding': np.fromstring(record['value_embedding'][1:-1], sep=',')
            }
            for record in result
        ]
    
    with driver.session() as session:
        stored_embeddings = session.execute_read(fetch_embeddings)
    
    # Calculate cosine similarity between the prompt and each stored embedding
    def cosine_similarity(vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    # Find the most relevant value based on similarity
    most_relevant_text = None
    highest_similarity = -1

    for embedding in stored_embeddings:
        similarity = cosine_similarity(prompt_embedding, embedding['key_embedding'])  # or embedding['value_embedding']
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_relevant_text = embedding['value']
    
    print('==> relevant text fetched')
    return most_relevant_text





# Combine the retrieved relevant texts and pass them to the LLM
# combined_text = " ".join(relevant_texts)
from llama_index.llms.ollama import Ollama
llm = Ollama(model="llama3", request_timeout=120.0)

def get_response(prompt):
    print('>>>>> getting response..')
    response = llm.stream_complete(prompt)
    for r in response:
        print(r.delta, end="")