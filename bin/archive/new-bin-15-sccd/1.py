import pandas as pd
from transformers import pipeline
import numpy as np

classifier = pipeline("zero-shot-classification", 
                     model="facebook/bart-large-mnli")

def categorize_text(text, categories):
    if pd.isna(text) or text == '':
        return 'unknown'
    
    try:
        result = classifier(str(text), categories)
        return result['labels'][0]
    except:
        return 'unknown'

df = pd.read_csv('data.csv')

categories = ['firewall', 'network', 'security', 'database', 'application', 'server']

df['_category'] = df['description'].apply(lambda x: categorize_text(x, categories))

df.to_csv('1.csv', index=False)
print('done')