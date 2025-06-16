import llm_response as llm
from neo4j_manager import Neo4jManager 
from functions.db_operations import delete_all_data
import rag as rag

print('Clearing data..')
delete_all_data('neo4j')
print('\n'*5)


db = Neo4jManager()
# Load data
db.embeddings_from_csv('./data/Alarms.csv', True)

# Get relevant data from the prompt
prompt = 'what is firstoccurence of NANP ?'
relevant_texts = str(db.return_prompt_specific_data('Alarms.csv',prompt))

# print(relevant_texts)
file_name = './data/DataToParse.txt'
with open(file_name, 'a') as file:
    file.write(relevant_texts)

rag.rag_model('DataToParse.txt', prompt)

# final_prompt = 'form this data ' + relevant_texts + ' answer this ' + prompt

# # Get response from llm
# llm.get_response("llama2", final_prompt)

# Clear data if required
print('\n'*4 + 'Clearing data..')
delete_all_data('neo4j')