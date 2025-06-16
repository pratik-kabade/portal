# rag_genai.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from ollama_api import get_llama2_response
from neo4j_db import Neo4jDB

def generate_embedding(text):
    # Dummy function to simulate text embedding generation
    res = np.random.rand(1, 768)
    return res

def retrieve_relevant_texts(query_embedding, embeddings, texts):
    if embeddings.size == 0:
        return []  # No embeddings to compare
    similarities = cosine_similarity(query_embedding, embeddings)
    relevant_texts = [texts[i] for i in similarities.argsort()[0][-3:]]  # Top 3 most similar texts
    return relevant_texts

def main():
    # Neo4j connection details
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "genesis"

    # Initialize Neo4jDB
    neo4j_db = Neo4jDB(uri, user, password)

    # Get user query
    query = "Explain the concept of RAG in GenAI"

    # Generate query embedding
    query_embedding = generate_embedding(query)
    # neo4j_db.save_embedding(query_embedding,query)

    # Retrieve stored embeddings and texts
    stored_data = neo4j_db.retrieve_embeddings()
    stored_embeddings = np.array([item[0] for item in stored_data])
    stored_texts = [item[1] for item in stored_data]

    # Check if there are any stored embeddings
    if stored_embeddings.size == 0:
        print("No stored embeddings found.")
        return

    # Reshape embeddings if necessary
    if len(stored_embeddings.shape) == 1:
        stored_embeddings = stored_embeddings.reshape(1, -1)

    # Retrieve relevant texts based on query embedding
    relevant_texts = retrieve_relevant_texts(query_embedding, stored_embeddings, stored_texts)

    # Check if relevant texts were found
    if not relevant_texts:
        print("No relevant texts found for the query.")
        return

    # Construct prompt for LLaMA2
    prompt = " ".join(relevant_texts) + " " + query

    # Get response from LLaMA2
    response = get_llama2_response(prompt)

    # Save query and its embedding to Neo4j
    neo4j_db.save_embedding(query_embedding, query)

    # Output the response
    print("Response:", response)

    # Close Neo4j connection
    neo4j_db.close()

if __name__ == "__main__":
    main()
