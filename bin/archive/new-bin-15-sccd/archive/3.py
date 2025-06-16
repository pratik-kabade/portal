import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def categorize_by_similarity(text, category_examples):
    if pd.isna(text) or text == '':
        return 'unknown'
    
    text_embedding = model.encode([str(text)])
    
    best_category = 'other'
    best_score = 0
    
    for category, examples in category_examples.items():
        example_embeddings = model.encode(examples)
        
        similarities = cosine_similarity(text_embedding, example_embeddings)
        max_similarity = np.max(similarities)
        
        if max_similarity > best_score:
            best_score = max_similarity
            best_category = category
    
    return best_category if best_score > 0.3 else 'other'  # Threshold for classification

category_examples = {
    'firewall': ['firewall configuration', 'blocking traffic', 'network security rules'],
    'network': ['network connectivity', 'router settings', 'IP configuration'],
    'security': ['security vulnerability', 'malware detection', 'encryption settings'],
    'database': ['database connection', 'SQL query', 'data storage'],
    'server': ['server maintenance', 'web server', 'hosting services']
}

df = pd.read_csv('data.csv')

df['_category'] = df['description'].apply(lambda x: categorize_by_similarity(x, category_examples))

df.to_csv('3.csv', index=False)
print('done')