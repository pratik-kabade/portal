import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables from .env file
load_dotenv()

username = 'neo4j'
password = 'genesis'
base_uri = 'http://localhost:7474'
# username = os.getenv("NEO4J_USER")
# password = os.getenv("NEO4J_PASSWORD")
# base_uri = os.getenv("NEO4J_BASEURL")

def create_database(database_name):
    url = f"{base_uri}/db/system/tx/commit"

    headers = {
        "Content-Type": "application/json"
    }

    query = {
        "statements": [
            {
                "statement": f"CREATE DATABASE {database_name}",
                "resultDataContents": []
            }
        ]
    }

    response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(username, password))

    if response.status_code == 200:
        print(f"Database '{database_name}' created successfully.")
    else:
        print("Failed to create database:", response.status_code, response.text)



def get_databases():
    url = f"{base_uri}/db/system/tx/commit"

    headers = {
        "Content-Type": "application/json"
    }

    query = {
        "statements": [
            {
                "statement": "SHOW DATABASES",
                "resultDataContents": ["row"]
            }
        ]
    }

    response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(username, password))

    if response.status_code == 200:
        result = response.json()
        # Print the raw result to debug the response structure
        # print("Raw response:", result)
        
        # Check if results are returned and print the databases
        if 'results' in result and result['results']:
            for record in result['results'][0]['data']:
                # Safely access database details
                row = record['row']
                db_name = row[0] if len(row) > 0 else "N/A"
                db_status = row[1] if len(row) > 1 else "N/A"
                db_size = row[2] if len(row) > 2 else "N/A"  # Size may not be available in all cases
                
                print(f"\nDatabase Name: {db_name}")
                print(f"Status: {db_status}")
                print(f"Size: {db_size}")
        else:
            print("No databases found or query did not return results.")
    else:
        print("Failed to retrieve databases:", response.status_code, response.text)



def get_database_data(database_name):
    url = f"{base_uri}/db/{database_name}/tx/commit"

    headers = {
        "Content-Type": "application/json"
    }

    query = {
        "statements": [
            {
                "statement": "MATCH (n) RETURN n LIMIT 25",
                "resultDataContents": ["row", "graph"]
            }
        ]
    }

    response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(username, password))

    if response.status_code == 200:
        result = response.json()
        # Print the raw result to debug the response structure
        # print("Raw response:", result)
        
        # Check if results are returned and print the data
        if 'results' in result and result['results']:
            for record in result['results'][0]['data']:
                # Safely access node details
                row = record['row']
                print(f"Node: {row}")
                print("-" * 40)
        else:
            print("No data found or query did not return results.")
    else:
        print("Failed to retrieve data:", response.status_code, response.text)


def delete_all_data(database_name):
    url = f"{base_uri}/db/{database_name}/tx/commit"

    headers = {
        "Content-Type": "application/json"
    }

    query = {
        "statements": [
            {
                "statement": "MATCH (n) DETACH DELETE n",
                "resultDataContents": []
            }
        ]
    }

    response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(username, password))

    if response.status_code == 200:
        print(f"All data from '{database_name}' deleted successfully.")
    else:
        print("Failed to delete data:", response.status_code, response.text)

# Example usage
# get_databases()
# create_database('new') #bug
# get_database_data("neo4j")
# delete_all_data("neo4j")