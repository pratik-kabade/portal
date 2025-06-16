from neo4j import GraphDatabase
from dotenv import load_dotenv
import pandas as pd
from llama_index.embeddings.ollama import OllamaEmbedding
import requests
from requests.auth import HTTPBasicAuth

# OBJECT is the name of database

class Neo4jManager:
    def __init__(self, username, password, uri, base_uri, llm_model, debug_mode=False):
        # Load environment variables from .env file
        load_dotenv()

        self.username = username
        self.password = password
        self.uri = uri
        self.base_uri = base_uri
        self.llm_model = llm_model
        self.debug_mode = debug_mode

        if self.debug_mode: print('> Initializing Neo4jManager..')

        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
        self.embed_model = OllamaEmbedding(
            model_name=self.llm_model,
            base_url="http://localhost:11434",
        )
        self.relation_used = 'CONTAINS'
        if self.debug_mode: print('=> Neo4jManager Initialized')


    def algo(self, prop, obj_name, value):        
        if self.debug_mode: print('> Creating algo..')
        algo = prop + ' of ' + obj_name + ' is ' + value
        return algo        
        
    def __str__(self):
        # Read all objects and return their details as a string
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT)
                RETURN p.name AS name, p.prop AS prop
                """
            )
            objects = [f"Name: {record['name']}" for record in result]
            return "\n".join(objects) if objects else "No objects found."

    def show_relationships(self):
        if self.debug_mode: print('> Showing relationships..')
        # Read all objects and their relationships, and return their details as a string
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT)-[r]->(object2:OBJECT)
                RETURN p.name AS name, p.prop AS prop, type(r) AS relationship, object2.name AS object2
                """
            )
            records = [f"1: {record['name']}, \n {record['relationship']} \n2: {record['object2']}" for record in result]
            return "\n\n".join(records) if records else "No objects found."

    def close(self):
        if self.debug_mode: print('> Closing driver..')
        self.driver.close()

    def create_object(self, name):
        if self.debug_mode: print('> Creating object..')
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (:OBJECT {name: $name})
                RETURN COUNT(*) AS count
                """,
                name=name
            )
            count = result.single()["count"]
            # print(f"Created {count} node.")
        if self.debug_mode: print('=> Object Created')

    def update_object(self, name, prop):
        if self.debug_mode: print('> Updating object..')
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT {name: $name})
                SET p.prop = $prop
                RETURN p
                """,
                name=name,
                prop=prop
            )
            summary = result.consume()
            # print(f"Query counters: {summary.counters}.")
        if self.debug_mode: print('=> Object Updated')

    def create_relationship(self, name, object2, relationship):
        if self.debug_mode: print('> Creating relationship..')
        with self.driver.session() as session:
            query = f"""
            MATCH (obj1:OBJECT {{name: $name}})
            MATCH (object2:OBJECT {{name: $object2}})
            CREATE (obj1)-[:{relationship}]->(object2)
            RETURN obj1, object2
            """
            result = session.run(query, name=name, object2=object2)
            summary = result.consume()
            # print(f"Query counters: {summary.counters}.")
        if self.debug_mode: print('=> Relationship Created')

    def delete_object(self, name):
        if self.debug_mode: print('> Deleting Object..')
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT {name: $name})
                DETACH DELETE p
                RETURN p
                """,
                name=name
            )
            summary = result.consume()
            # print(f"Query counters: {summary.counters}.")
        if self.debug_mode: print('=> Object Deleted')

    def build_from_csv(self, file):
        if self.debug_mode: print('> Building from CSV..')
        data = pd.read_csv(file)
        header = data.columns.to_numpy()
        for row in range(len(data)):
            first_row_dict = data.iloc[row].to_dict()
            first_element = first_row_dict[header[0]]
            self.create_object(first_element)

            for col in range(len(header)):
                col_name = header[col]
                value = first_row_dict[header[col]]
                # print(first_row_dict[header[0]] ,'|||', col_name ,'|||', value)

                with self.driver.session() as session:
                    query = f"""
                    MATCH (p:OBJECT {{name: $name}})
                    SET p.{col_name} = $value
                    RETURN p
                    """
                    result = session.run(query, name=first_row_dict[header[0]], value=value)
                    summary = result.consume()

                    # print(f"Query counters: {summary.counters}.")
        if self.debug_mode: print('> Data Build from CSV completed!')

    def embeddings_from_csv(self, file, show_progress=False):        
        if self.debug_mode: print('> Building Embeddings from CSV..')
        lead_object = file.split('/')[-1]
        # print(lead_object)
        self.create_object(lead_object)

        data = pd.read_csv(file)
        header = data.columns.to_numpy()

        progress = len(data)
        for row in range(len(data)):
            first_row_dict = data.iloc[row].to_dict()
            first_element = str(first_row_dict[header[0]])
            self.create_object(first_element)
            self.create_relationship(lead_object, first_element, self.relation_used)

            sentences = ''
            for col in range(len(header)):
                col_name = str(header[col])
                value = str(first_row_dict[header[col]])

                sentence = self.algo(prop=col_name, obj_name=first_element, value=value) 
                # print(sentence)
                sentences += sentence + ', '

                with self.driver.session() as session:
                    query = f"""
                    MATCH (p:OBJECT {{name: $name}})
                    SET p.{col_name} = $value
                    RETURN p
                    """
                    result = session.run(query, name=first_element, value=value)
                
                    summary = result.consume()

                    # print(f"Query counters: {summary.counters}.")

            key_embedding = self.embed_model.get_query_embedding(sentences)
            s = str(sentences)
            with self.driver.session() as session:
                query = """
                MATCH (p:OBJECT {name: $name})
                SET p.sentences = $sentences
                RETURN p
                """
                result = session.run(query, name=first_element, sentences=s)

                summary = result.consume()
                # print(f"Query counters: {summary.counters}.")

            if show_progress: print(str(progress) + ' item(s) left..')
            progress -= 1
        if self.debug_mode: print('=> Embeddings Build from CSV completed!')
        print()

    def return_prompt_specific_data(self, object_name, prompt):
        if self.debug_mode: print('> Returning prompt specific data..')
        def list_all_nodes(object_name):
            if self.debug_mode: print('> Listing all nodes..')
            nodes = []
            with self.driver.session() as session:
                query = """
                MATCH (p:OBJECT {name: $object_name})-[r]->(object2:OBJECT)
                RETURN type(r) AS relationship_type, object2.name AS object2
                """
                result = session.run(query, object_name=object_name)
                records = [f"{record['object2']}" for record in result]
                nodes = records

            return nodes if len(nodes)!=0 else f"No relationships found for '{object_name}'."

        item_list = list_all_nodes(object_name)
        lowered_item_list = [i.lower() for i in item_list]
        lowered = prompt.lower().split(' ')
        item = ''

        for i in lowered:
            if i in lowered_item_list:
                item = i
        for i in range(len(item_list)):
            if lowered_item_list[i] == item:
                item = item_list[i]

        # all_properties = self.find_by_property(object_name=item, property_type='sentences')

        if item != '':
            print('Item found!')
            return self.find_by_property(object_name=item, property_type='sentences')  
        else:
            print('NOT found!')
            return self.return_all_data(object_name=object_name)

    def return_all_data(self, object_name):
        if self.debug_mode: print('> Returning all data..')
        def list_all_nodes(object_name):
            if self.debug_mode: print('> Listing all nodes..')
            nodes = []
            with self.driver.session() as session:
                query = """
                MATCH (p:OBJECT {name: $object_name})-[r]->(object2:OBJECT)
                RETURN type(r) AS relationship_type, object2.name AS object2
                """
                result = session.run(query, object_name=object_name)
                records = [f"{record['object2']}" for record in result]
                nodes = records

            return nodes if len(nodes)!=0 else f"No relationships found for '{object_name}'."

        item_list = list_all_nodes(object_name)

        all_properties = []
        for item in item_list:
            all_properties.append(self.find_by_property(object_name=item, property_type='sentences'))

        return all_properties



    # DB_Ops
    def db_op_create_database(self, database_name): #BUG
        if self.debug_mode: print('> DB-Operation: Creating Database..')
        url = f"{self.base_uri}/db/system/tx/commit"
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
        response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code == 200:
            print(f"Database '{database_name}' created successfully.")
        else:
            print("Failed to create database:", response.status_code, response.text)

    def db_op_get_databases(self):
        if self.debug_mode: print('> DB-Operation: getting all databases..')
        url = f"{self.base_uri}/db/system/tx/commit"
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
        response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code == 200:
            result = response.json()
            # print("Raw response:", result)
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

    def db_op_get_database_data(self, database_name):
        if self.debug_mode: print('> DB-Operation: getting database data..')
        url = f"{self.base_uri}/db/{database_name}/tx/commit"
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
        response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code == 200:
            result = response.json()
            # print("Raw response:", result)
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

    def delete_all_data(self, database_name):
        if self.debug_mode: print('> DB-Operation: deleting database..')
        url = f"{self.base_uri}/db/{database_name}/tx/commit"
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
        response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code == 200:
            print(f"All data from '{database_name}' deleted successfully.")
        else:
            print("Failed to delete data:", response.status_code, response.text)



    # Filters
    def find_object(self, name):
        if self.debug_mode: print('> Filters: finding object..')
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT {name: $name})
                OPTIONAL MATCH (p)-[r]->(object2:OBJECT)
                RETURN p.name AS name, p.prop AS prop, collect({relationship: type(r), object2: object2.name}) AS relationships
                """,
                name=name
            )
            record = result.single()
            if record:
                object_details = f"Name: {record['name']}\nProperty: {record['prop']}"
                if record['relationships']:
                    relationships = "\n".join(
                        [f"R: {rel['relationship']}, \nObject2: {rel['object2']}\n" for rel in record['relationships']]
                    )
                    object_details += f"\n\nRelationships:\n{relationships}"
                return object_details
            else:
                return f"OBJECT with name '{name}' not found."

    def find_by_relationship(self, object2, relationship_type):
        if self.debug_mode: print('> Filters: finding relationship..')
        with self.driver.session() as session:
            query = f"""
            MATCH (p:OBJECT)-[r:{relationship_type}]->(object2:OBJECT {{name: $object2}})
            RETURN p.name AS name, p.prop AS prop
            """
            result = session.run(query, object2=object2)
            records = [f"Name: {record['name']}" for record in result]
            return "\n".join(records) if records else f"No objects found with relationship '{relationship_type}' to '{object2}'."

    def find_by_property(self, object_name, property_type):
        if self.debug_mode: print('> Filters: finding property..')
        with self.driver.session() as session:
            query = """
            MATCH (p:OBJECT {name: $object_name})
            RETURN p
            """
            result = session.run(query, object_name=object_name)
            records = [record["p"] for record in result]
            if not records:
                return f"No properties found for '{object_name}'."
            
            property_values = [record[property_type] for record in records if property_type in record]
            if not property_values:
                return f"No properties of type '{property_type}' found for '{object_name}'."
            
            return property_values

    def find_all_relationships(self, object_name):
        if self.debug_mode: print('> Filters: finding all relationship..')
        with self.driver.session() as session:
            query = """
            MATCH (p:OBJECT {name: $object_name})-[r]->(object2:OBJECT)
            RETURN type(r) AS relationship_type, object2.name AS object2
            """
            result = session.run(query, object_name=object_name)
            records = [f"Relationship: {record['relationship_type']}, Object2: {record['object2']}" for record in result]
            return "\n".join(records) if records else f"No relationships found for '{object_name}'."

    def find_all_properties(self, object_name):
        if self.debug_mode: print('> Filters: finding all properties..')
        with self.driver.session() as session:
            query = """
            MATCH (p:OBJECT {name: $object_name})
            RETURN p
            """
            result = session.run(query, object_name=object_name)
            records = [record["p"] for record in result]
            return records if records else f"No properties found for '{object_name}'."


# Example usage
if __name__ == "__main__":
    username = 'neo4j'
    password = 'genesis'
    uri = 'bolt://localhost:7687'
    base_uri = 'http://localhost:7474'
    llm_model = 'llama3'

    db = Neo4jManager(username, password, uri, base_uri, llm_model)

    # db.create_object("DeviceID1")
    # db.create_object("AlarmID1")
    # db.create_object("AlarmID2")
    # db.create_object("AlarmID3")
    # db.create_object("TTID1")
    # db.create_object("TTID2")

    # db.create_relationship("DeviceID1", "AlarmID1", "HAS_ALARM")
    # db.create_relationship("DeviceID1", "AlarmID2", "HAS_ALARM")
    # db.create_relationship("DeviceID1", "AlarmID3", "HAS_ALARM")
    # db.create_relationship("AlarmID1", "TTID1", "HAS_TT")
    # db.create_relationship("AlarmID3", "TTID2", "HAS_TT")
    # db.create_relationship("DeviceID1", "TTID1", "HAS_TT")
    # db.create_relationship("DeviceID1", "TTID2", "HAS_TT")
    # db.create_relationship("DeviceID1", "TTID2", "HAS_TT2")

    # db.update_object("AlarmID3", 'Closed')

    # print(db)
    # print(db.show_relationships())
    # print(db.find_object('DeviceID1'))
    # print(db.find_by_relationship("TTID2", "HAS_TT2"))

    # db.build_from_csv('./data/Alarms.csv')
    # print(db)
    # db.embeddings_from_csv('./data/Alarms.csv')
    # print(db.find_all_properties('HETN'))
    # print(db.find_all_relationships('HETN'))
    # print(db.list_all_nodes('Alarms.csv'))
    # print(db.find_by_property('ADIQ', 'Northings'))
    # print(db.find_by_property('HETN', 'FirstOccurrence'))

    # prompt = 'what is NANP ?'

    # print(db.return_prompt_specific_data('Alarms.csv',prompt))
    # db.return_all_data('Alarms.csv')


    # Close the connection
    db.close()
