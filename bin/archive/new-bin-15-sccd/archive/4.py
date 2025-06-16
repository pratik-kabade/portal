import pandas as pd
from transformers import pipeline

df = pd.read_csv('data.csv')

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
categories = ['firewall', 'database', 'network', 'security', 'server']

def classify_row(text):
    result = classifier(text, categories)
    return result['labels'][0]

df['_category'] = df['description'].apply(classify_row)

df.to_csv('4.csv', index=False)
print('done')