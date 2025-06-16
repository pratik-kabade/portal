# neo4j_db.py
from neo4j import GraphDatabase
import logging
import numpy as np

class Neo4jDB:
    def __init__(self, uri, user, password):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception as e:
            logging.error(f"Failed to create Neo4j driver: {e}")
            raise

    def close(self):
        if self.driver:
            self.driver.close()


    def save_embedding(self, embedding, text):
        try:
            print("Saving embedding to Neo4j...")
            
            # Convert the embedding to a list of floats if it is a NumPy array
            if isinstance(embedding, np.ndarray):
                embedding_list = embedding.flatten().tolist()  # Flatten and convert to list
            else:
                embedding_list = embedding

            # # Print the type and content of embedding_list for debugging
            # print(f"Embedding list type: {type(embedding_list)}")
            # print(f"Embedding list content: {embedding_list}")

            # Ensure embedding_list is a flat list of primitives
            if not isinstance(embedding_list, list) or not all(isinstance(i, (int, float)) for i in embedding_list):
                raise ValueError("Embedding must be a list of primitive types (int or float).")
            
            with self.driver.session() as session:
                session.run(
                    "CREATE (e:Embedding {embedding: $embedding, text: $text})",
                    embedding=embedding_list,
                    text=text
                )
            print("Embedding saved successfully.")
        except Exception as e:
            print(f"Failed to save embedding: {e}")
            raise


    def retrieve_embeddings(self):
        # print('=> Retrieving..')
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (e:Embedding) RETURN e.embedding AS embedding, e.text AS text")
                # print([(record["embedding"], record["text"]) for record in result])
                return [(record["embedding"], record["text"]) for record in result]
        except Exception as e:
            logging.error(f"Failed to retrieve embeddings: {e}")
            raise
