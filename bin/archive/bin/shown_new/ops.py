from neo4j_manager import Neo4jManager 
from llm import rag_model, get_response
import os

username = os.getenv("NEO4J_USER", 'neo4j')
password = os.getenv("NEO4J_PASSWORD", 'genesis')
uri = os.getenv("NEO4J_URI", 'bolt://localhost:7687')
base_uri = os.getenv("NEO4J_BASEURL", 'http://localhost:7474')
llm_model = os.getenv("LLM_MODEL", 'llama3')

db = Neo4jManager(username, password, uri, base_uri, llm_model, True)


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

# prompt3 = 'what is firstoccurence of 4115'
# relevant_texts3 = db.return_prompt_specific_data('f1.csv', prompt3, 'RESID')
# print(3, relevant_texts3) # RES2

# relevant_texts4 = db.return_prompt_specific_data('f2.csv', relevant_texts3, 'desc')
# print(4, relevant_texts4) # A12desc


db.merge_data('a', 'b')

# file_path = './data/'
# file_name = 'DataToParse.txt'
# with open(file_path+file_name, 'a') as file:
#     file.write(relevant_texts)
# print('Saved text file, proceeding ahead with RAG')

# rag_model(file_name, prompt)

# final_prompt = 'form this data ' + str(relevant_texts2) + ' answer this ' + prompt2
# get_response(final_prompt)

# # Clear data if required
# print('\n'*4 + 'Clearing data..')
# db.delete_all_data('neo4j')