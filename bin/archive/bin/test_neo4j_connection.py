# test_save_embedding.py
from neo4j_db import Neo4jDB
import numpy as np

def test_save_embedding():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "genesis"

    neo4j_db = Neo4jDB(uri, user, password)

    # Test data
    embedding = np.random.rand(1, 768)
    text = "Sample embedding"

    try:
        neo4j_db.save_embedding(embedding, text)
        print("Test embedding saved successfully.")
    except Exception as e:
        print(f"Test error saving embedding: {e}")
    finally:
        neo4j_db.close()

if __name__ == "__main__":
    test_save_embedding()
