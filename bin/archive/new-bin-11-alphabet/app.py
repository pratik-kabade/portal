from llm_settings import LLM
import pandas as pd


llm_model = 'llama3.1'
llm_instance = LLM(llm_model=llm_model, debug_mode=False)

df = pd.read_csv('data/dummy-jira.csv')
temp = 'Issue observed: ; Steps to reproduce: ; Expected result: ;'
incomplete_bugs={}

def run_llm():
    for index, row in df.iterrows():
        r=row['Description']
        p=(f'''from the below description 
        description:{r} 
        tell me if the Issue observed, Steps to reproduce, Expected result are filled or not 
        just tell me it in yes or no only''')
        res = llm_instance.fetch_entire_response(p)
        if (res == 'No'):
            print(row['Bug ID'])
            incomplete_bugs[row['Bug ID']] = row['Component']

for _ in range(5):
    run_llm()
    print('done')

results = {}

df2 = pd.read_csv('data/random_persons.csv')
for bug_id, component in incomplete_bugs.items():
    person = df2[df2['Component'] == component]
    assignee = person['Name'].values[0]
    email = person['Email'].values[0]
    print(f"Bug ID: {bug_id}, Component: {component}, Assignee: {assignee}, Email: {email}")
    results[len(results)] = {'Bug ID': {bug_id}, 'Component': {component}, 'Assignee': {assignee}, 'Email': {email}}

# print(results)