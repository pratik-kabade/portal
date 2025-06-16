import llm_response as llm
from neo4j_manager import Neo4jManager 
from functions.db_operations import delete_all_data


print('Clearing data..')
delete_all_data('neo4j')
print('\n'*5)


db = Neo4jManager()
# Load data
db.embeddings_from_csv('./data/Alarms.csv', True)

# Get relevant data from the prompt
prompt = 'what is firstoccurence of NANP ?'
relevant_texts = str(db.return_prompt_specific_data('Alarms.csv',prompt))

final_prompt = 'form this data ' + relevant_texts + ' answer this ' + prompt

# print(final_prompt)

# Get response from llm
llm.get_response("llama2", final_prompt)

# Clear data if required
print('\n'*4 + 'Clearing data..')
delete_all_data('neo4j')