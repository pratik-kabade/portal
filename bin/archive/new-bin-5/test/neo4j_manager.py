from neo4j import GraphDatabase
from dotenv import load_dotenv
import pandas as pd
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
        self.logs = ''

        self.log_manager('init-neo4j')

        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
        self.relation_used = 'CONTAINS'
        self.log_manager('init-neo4j-done')

    def log_manager(self, fn, v1='', v2='', v3=''):
        if self.debug_mode:
            log_messages = {
                "init-neo4j": '> Initializing Neo4jManager..',
                "init-neo4j-done": '=> Neo4jManager Initialized\n',
                "algo": '> Creating algo...',
                "show-rel": '> Showing relationships..',
                "close": '=> Driver closed\n',
                "create": f'> Creating object "{v1}"..',
                "create-done": f'=> Object Created "{v1}"\n',
                "create-prop": f'> Creating property->"{v1}" for "{v2}" as "{v3}"..',
                "create-prop-done": f'=> Property created->"{v1}" for "{v2}" as "{v3}"\n',
                "create-rel": f'> Creating relationship "{v1}" for "{v2}" with "{v3}"..',
                "create-rel-done": f'=> Relationship created "{v1}" for "{v2}" with "{v3}"\n',
                "delete-obj": f'> Deleting Object "{v1}"..',
                "delete-obj-done": f'=> Object Deleted "{v1}"\n',
                "build-csv": f'> Building from CSV, "{v1}"..',
                "build-csv-done": f'=> Embeddings Build from CSV, "{v1}" completed!\n',
                "list-all-node": f'> Listing all nodes for "{v1}"..',
                "return-prompt-sp": f'> Returning prompt "{v2}" specific data for object "{v1}"..',
                "item-found": 'Item found from the prompt!',
                "return-all": f'> Returning all data for "{v1}"..',
                "query1": f'> Querying "{v1}",[obj2] (=>) on "{v2}",[OBJ1]..',
                "query2": f'-----> Value of "{v1}" is "{v2}"',
                "query3": f'-----> "{v1}" of "{v2}" is "{v3}"',
                "merge": f'> Merging "{v1}",[file2] (=>) on "{v2}",[FILE1]..',
                "merge-done": f'=> Merged "{v1}",[file2] (=>) on "{v2}",[FILE1]\n',
                "db-create": '> DB-Operation: Creating Database..',
                "db-create-done": '=> DB-Operation: database created\n',
                "db-get-all": '> DB-Operation: getting all databases..',
                "db-get": '> DB-Operation: getting database data..',
                "db-delete": '> DB-Operation: deleting database..',
                "db-delete-done": '=> DB-Operation: database deleted\n',
                "find-obj": f'> Filters: finding object "{v1}"..',
                "find-rel": f'> Filters: finding relationship of "{v1}"..',
                "find-prop": f'> Filters: finding property of "{v1}"..',
                "find-all-rel": f'> Filters: finding all relationships of "{v1}"..',
                "find-all-prop": f'> Filters: finding all properties of "{v1}"..',
            }
            
            log = log_messages.get(fn, '> Default logging')
                        
            if fn == "close":
                with open('logs.txt', 'w') as file:
                    file.write(self.logs)

            self.logs += log + '\n'
            # print(log)

    def algo(self, prop, obj_name, value):        
        self.log_manager('algo')
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
            return "\n".join(objects) if objects else "No objects found.\n"

    def show_relationships(self):
        self.log_manager('show-rel')
        # Read all objects and their relationships, and return their details as a string
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT)-[r]->(object2:OBJECT)
                RETURN p.name AS name, p.prop AS prop, type(r) AS relationship, object2.name AS object2
                """
            )
            records = [f"1: {record['name']}, \n {record['relationship']} \n2: {record['object2']}" for record in result]
            return "\n\n".join(records) if records else "No objects found.\n"

    def close(self):
        self.driver.close()
        self.log_manager('close')

    def create_object(self, name):
        self.log_manager('create', v1=name)
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
        self.log_manager('create-done', v1=name)

    def create_property(self, name, prop, value):
        self.log_manager('create-prop', v1=prop, v2=name, v3=value)

        # Construct the Cypher query with dynamic property names
        query = f"""
        MATCH (p:OBJECT {{name: $name}})
        SET p.{prop} = $value
        RETURN p
        """

        with self.driver.session() as session:
            result = session.run(query, name=name, value=value)
            summary = result.consume()
            # print(f"Query counters: {summary.counters}.")
        self.log_manager('create-prop-done', v1=prop, v2=name, v3=value)

    def create_relationship(self, name, object2, relationship):
        self.log_manager('create-rel', v1=relationship, v2=name, v3=object2)
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
        self.log_manager('create-rel-done', v1=relationship, v2=name, v3=object2)

    def delete_object(self, name):
        self.log_manager('delete-obj', v1=name)
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
        self.log_manager('delete-obj-done', v1=name)

    def build_from_csv(self, file, show_progress=False):        
        self.log_manager('build-csv', v1=file)
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
                self.create_property(first_element,col_name,value)

            s = str(sentences)
            self.create_property(first_element,'sentences',s)
            if show_progress: print(str(progress) + ' item(s) left..')
            progress -= 1
        self.log_manager('build-csv-done', v1=file)

    def list_all_nodes(self, object_name):
        self.log_manager('list-all-node',v1=object_name)
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

    def return_prompt_specific_data(self, object_name, prompt, prop='sentences'):
        self.log_manager('return-prompt-sp', v1=object_name, v2=prompt)
        item_list = self.list_all_nodes(object_name)
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
            self.log_manager('item-found')
            result = self.find_by_property(object_name=item, property_type=prop)
            return result[0] if len(result)==1 else result
        else:
            print('NO item found from the prompt!')
            return self.return_all_data(object_name=object_name)

    def return_all_data(self, object_name):
        self.log_manager('return-all', v1=object_name)
        item_list = self.list_all_nodes(object_name)

        all_properties = []
        for item in item_list:
            all_properties.append(self.find_by_property(object_name=item, property_type='sentences'))

        return all_properties

    def query_data_by_key(self, primary_object, primary_key, secondary_property):
        self.log_manager('query1', v1=secondary_property, v2=primary_object)
        primary_key_value = self.find_by_property(primary_object, primary_key)
        self.log_manager('query2', v1=primary_key, v2=primary_key_value)
        secondary_property_value = []
        if type(primary_key_value) == list:
            for i in primary_key_value:
                secondary_property_value.append(self.find_by_property(i, secondary_property))
        else:
            secondary_property_value.append(self.find_by_property(primary_key_value, secondary_property))
        self.log_manager('query3', v1=secondary_property, v2=primary_object, v3=secondary_property_value)
        return secondary_property_value

    def merge_properties(self, FILE1, file2, primary_key, show_progress=False):
        self.log_manager('merge', v1=file2, v2=FILE1)
        FILE1_nodes = self.list_all_nodes(FILE1)
        file2_nodes = self.list_all_nodes(file2)
        progress = len(FILE1_nodes)
        for FILE1_node in FILE1_nodes:
            FILE1_ids = self.find_by_property(FILE1_node, primary_key)
            
            for file1_id in FILE1_ids:
                ID = str(file1_id)
                index = -1

                # Find ID from file2_nodes
                for idx, node in enumerate(file2_nodes):
                    properties = self.find_all_properties(node)
                    found = False
                    for key, value in properties.items():
                        if key == primary_key and value == ID:
                            index = idx
                            found = True
                            break
                    if found:
                        break
                            
                # Avoid creating duplicate keys
                dict = self.find_all_properties(FILE1_node)
                old_items = []
                for k,v in dict.items():
                    old_items.append(k)
                    
                # Indexing
                item_to_change = file2_nodes[index]
                dict = self.find_all_properties(item_to_change)
                if index != -1:                
                    for k,v in dict.items():                    
                        if k not in old_items:
                            self.create_property(FILE1_node,k,v)
                else:
                    print(f"No matching '{primary_key}' found for '{ID}' in '{file2}'")
            if show_progress: print(str(progress) + ' item(s) left..')
            progress -= 1

        self.log_manager('merge-done', v1=file2, v2=FILE1)



    # DB_Ops
    def db_op_create_database(self, database_name): #BUG
        self.log_manager('db-create')
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
            self.log_manager('db-create-done')
        else:
            print("Failed to create database:", response.status_code, response.text)

    def db_op_get_databases(self):
        self.log_manager('db-get-all')
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
        self.log_manager('db-get')
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
        self.log_manager('db-delete')
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
            self.log_manager('db-delete-done')
        else:
            print("Failed to delete data:", response.status_code, response.text)



    # Filters
    def find_object(self, name):
        self.log_manager('find-obj', v1=name)
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
        self.log_manager('find-rel',v1=object2)
        with self.driver.session() as session:
            query = f"""
            MATCH (p:OBJECT)-[r:{relationship_type}]->(object2:OBJECT {{name: $object2}})
            RETURN p.name AS name, p.prop AS prop
            """
            result = session.run(query, object2=object2)
            records = [f"Name: {record['name']}" for record in result]
            return "\n".join(records) if records else f"No objects found with relationship '{relationship_type}' to '{object2}'."

    def find_by_property(self, object_name, property_type):
        self.log_manager('find-prop',v1=object_name)
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
        self.log_manager('find-all-rel',v1=object_name)
        with self.driver.session() as session:
            query = """
            MATCH (p:OBJECT {name: $object_name})-[r]->(object2:OBJECT)
            RETURN type(r) AS relationship_type, object2.name AS object2
            """
            result = session.run(query, object_name=object_name)
            records = [f"Relationship: {record['relationship_type']}, Object2: {record['object2']}" for record in result]
            return "\n".join(records) if records else f"No relationships found for '{object_name}'."

    def find_all_properties(self, object_name):
        self.log_manager('find-all-prop',v1=object_name)
        with self.driver.session() as session:
            query = """
            MATCH (p:OBJECT {name: $object_name})
            RETURN p
            """
            result = session.run(query, object_name=object_name)
            
            # Extract the properties from the node
            properties = {}
            for record in result:
                node = record["p"]
                properties = dict(node)  # Convert the node's properties to a dictionary
            
            return properties if properties else f"No properties found for '{object_name}'."


# Example usage
if __name__ == "__main__":
    username = 'neo4j'
    password = '123'
    uri = 'bolt://localhost:7687'
    base_uri = 'http://localhost:7474'
    llm_model = 'llama2'

    db = Neo4jManager(username, password, uri, base_uri, llm_model, True)

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

    # # db.build_from_csv('./data/Alarms.csv')
    # db.build_from_csv('./data/f1.csv')
    # db.build_from_csv('./data/f2.csv')
    # print(db.query_data_by_key(primary_object='4115', primary_key='RESID', secondary_property='desc', 
    #                           _file1='f1.csv', _file2='f2.csv'))
    # print(db.find_by_property('RES1', 'RESID'))
    # print(db)
    # db.build_from_csv('./data/Alarms.csv')
    # print(db.find_all_properties('HETN'))
    # print(db.find_all_relationships('HETN'))
    # print(db.list_all_nodes('Alarms.csv'))
    # print(db.find_by_property('ADIQ', 'Northings'))
    # print(db.find_by_property('HETN', 'FirstOccurrence'))

    # prompt = 'what is NANP ?'

    # print(db.return_prompt_specific_data('Alarms.csv',prompt))
    # db.return_all_data('Alarms.csv')

    # db.delete_all_data('neo4j')
    # file1 = 'employees.csv'
    # file2 = 'compensation.csv'
    # file3 = 'work_experience.csv'
    # pk = 'id'
    # db.build_from_csv('data/sample/compensation.csv')
    # db.build_from_csv('data/sample/employees.csv')
    # db.build_from_csv('data/sample/work_experience.csv')
    # db.merge_properties(file1, file2, pk)
    # db.merge_properties(file1, file3, pk, True)
    # print(db.find_by_property('Charlie', 'description'))

    # db.delete_all_data('neo4j')
    # Close the connection
    db.close()