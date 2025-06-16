from functions.neo4j_manager import Neo4jManager 
from functions.db_operations import delete_all_data
from functions.rag import rag_model

# print('Clearing data..')
# delete_all_data('neo4j')
# print('\n'*5)


db = Neo4jManager()
# # Load data
# db.embeddings_from_csv('./data/Alarms.csv', True)

# Get relevant data from the prompt
# prompt = 'what is firstoccurence of NANP ?'
prompt = 'who have Mar 10, 2024, 8:10:20 AM as lastoccurence?'
relevant_texts = str(db.return_prompt_specific_data('Alarms.csv', prompt))
# all_texts = str(db.return_all_data('Alarms.csv'))

file_path = './data/'
file_name = 'DataToParse.txt'
with open(file_path+file_name, 'a') as file:
    file.write(relevant_texts)
print('Saved text file, proceeding ahead with RAG')

rag_model(file_name, prompt)


# # Clear data if required
# print('\n'*4 + 'Clearing data..')
# delete_all_data('neo4j')