from neo4j_manager import Neo4jManager 
from llm import LLM
import os

username = os.getenv("NEO4J_USER", 'neo4j')
password = os.getenv("NEO4J_PASSWORD", 'genesis')
uri = os.getenv("NEO4J_URI", 'bolt://localhost:7687')
base_uri = os.getenv("NEO4J_BASEURL", 'http://localhost:7474')
llm_model = os.getenv("LLM_MODEL", 'llama3')

db = Neo4jManager(username, password, uri, base_uri, llm_model)


# print('Clearing data..')
# db.delete_all_data('neo4j')
# print('\n'*5)


# # Load data
# db.build_from_csv('./data/f1.csv', True)
# db.build_from_csv('./data/f2.csv', True)

# prompt1 = 'what is firstoccurence of 4115'
# relevant_texts1 = db.return_prompt_specific_data('f1.csv', prompt1)
# print(1, relevant_texts1)  # everything related 4115

# prompt2 = 'who have Mar 10, 2024, 8:10:20 AM as lastoccurence?'
# relevant_texts2 = db.return_prompt_specific_data('f1.csv', prompt2)
# print(2, relevant_texts2) # everything

prompt3 = 'what is desc of 4115'
relevant_texts3 = db.return_prompt_specific_data('f1.csv', prompt3, 'RESID')
print(3, relevant_texts3) # RES2

relevant_texts4 = db.return_prompt_specific_data('f2.csv', relevant_texts3, 'desc')
print(4, relevant_texts4) # A12desc

print(db.query_data_by_key(
    primary_object='4115', 
    primary_key='RESID', 
    secondary_property='desc', 
    _file1='f1.csv', 
    _file2='f2.csv'
    ))

# file_path = './data/'
# file_name = 'DataToParse.txt'
# with open(file_path+file_name, 'a') as file:
#     file.write(relevant_texts)
# print('Saved text file, proceeding ahead with RAG')

# rag_model(file_name, prompt)

# final_prompt = 'form this data ' + str('relevant_texts2') + ' answer this ' + 'prompt2'
# llm1=LLM(llm_model='llama3', debug_mode=True)
# llm1.rag_model('/f1.csv', 'what is first occurence of nanp')
# llm1.get_response('hi')

# # Clear data if required
# print('\n'*4 + 'Clearing data..')
# db.delete_all_data('neo4j')