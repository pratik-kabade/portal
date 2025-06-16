import pandas as pd
import re

def categorize_by_keywords(text):
    if pd.isna(text):
        return 'unknown'
    
    text_lower = str(text).lower()
    
    categories = {
        'firewall': ['firewall', 'iptables', 'ufw', 'pfsense', 'fortinet', 'checkpoint'],
        'network': ['network', 'router', 'switch', 'ethernet', 'tcp', 'udp', 'ip'],
        'security': ['security', 'antivirus', 'malware', 'encryption', 'ssl', 'tls'],
        'database': ['database', 'mysql', 'postgresql', 'mongodb', 'sql', 'oracle'],
        'server': ['server', 'apache', 'nginx', 'iis', 'tomcat', 'hosting'],
        'application': ['application', 'software', 'program', 'app', 'service']
    }
    
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    
    return 'other'

df = pd.read_csv('data.csv')

df['_category'] = df['description'].apply(categorize_by_keywords)

df.to_csv('2.csv', index=False)
print('done')