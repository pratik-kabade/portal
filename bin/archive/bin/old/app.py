import app2 as app2

path='/home/genaidevassetv1/portal/data/Alarms.csv'
dicts=app2.fetchdata(path)
embeddings=app2.creating_embeddings(dicts)
app2.saving_in_graphdb(embeddings)
# app2.saving_in_graphdb(embeddings, 'alarms')


prompt="what is FirstOccurrence of HETN?"
relevant_texts=app2.get_relevant_text(prompt)
# relevant_texts=app2.get_relevant_text(prompt, 'alarms')

final_prompt = 'form this data ' + relevant_texts + ' answer this ' + prompt
# print(relevant_texts)
app2.get_response(final_prompt)

print('\nclearing data now..')
from functions.db_operations import delete_all_data
delete_all_data('neo4j')