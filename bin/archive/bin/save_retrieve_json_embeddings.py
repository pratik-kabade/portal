import os
from functions.crud import Neo4jManager
import json

db = Neo4jManager()
folder_path = "/home/genaidevassetv1/portal/data/vectordb/"
folder_path2 = "/home/genaidevassetv1/portal/data/vectordb2/"
RELATIONSHIP = 'has'
PROPERTY = 'contains'

def create_nodes_and_relationships():
    db.create_object('ABC')

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        db.create_object(filename)
        db.create_relationship('ABC', filename, RELATIONSHIP)
        
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                content = str(file.read())
            db.update_properties(filename, PROPERTY, content)
        print(f'^ Stored {file} into neo4j')

    print("========> Nodes-Relationships created successfully!")

create_nodes_and_relationships()


def create_files():
    data = db.find_all_relationships('ABC').split('\n')
    files = []
    for name in data:
        file_name=name.split(f'Relationship: {RELATIONSHIP}, Object2: ')[1]
        files.append(file_name)
        
    if not os.path.exists(folder_path2):
        os.makedirs(folder_path2)

    num = 1
    for file in files:
        file_path = os.path.join(folder_path2, file)
        a = str(db.find_all_properties(file))
        # <Node element_id='32' labels=frozenset({'OBJECT'}) properties={'contains': 'content', 'name': 'default__vector_store.json'}>]
        b = str(a.split(PROPERTY + "': '")[1])
        # content', 'name': 'index_store.json'}>]
        c = str(b.split("', ")[0])
        # print(c)
        # json_data = json.loads(c)
        # print('\n\n\n\n', json_data)

        # Write the content to the file
        with open(file_path, 'w') as file:
            file.write(c)
        print(f'========> Created {num} file')
        num += 1


create_files()

# print(db.find_all_relationships('ABC'))
# print(db.find_all_relationships('index_store.json'))