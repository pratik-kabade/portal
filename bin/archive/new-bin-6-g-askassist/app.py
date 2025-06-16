import os
import requests
from jira import JIRA
import json

JIRA_SERVER='https://iotpegenai.atlassian.net'
JIRA_USERNAME='anurag.agr@gmail.com'
JIRA_API_TOKEN='ATATT3xFfGF0rnMzi2atAgf0Q2uB53QnEpqSQqVmlmvg-sNUP0SPJpfojx4K208Vn-mcN7w7sT1wq1Gxhuh76aN0z0RcKj8zkKjM6G0W4IIMnDS_5kSvUy7tr2L1MUTdj6CtJaiWskoZ0pej_YdYhySWyk7z39mCkNsGqxOCtbhAkfHX1_VXgeY=8EE448A4'


PROJECT_KEY = "RDKB"
AUTH = (JIRA_USERNAME, JIRA_API_TOKEN)

def get_userstories(ProjectKey):
    try:
        url = f'{JIRA_SERVER}/rest/api/3/search?fields=issue,summary,issuetype&jql=project={ProjectKey}'
        headers = {'Content-Type': 'application/json'}

        response = requests.get(url, headers=headers, auth=AUTH)
        response.raise_for_status()
        issues = []

        for issue in response.json().get('issues', []):
            if issue['fields']['issuetype']['name'] == 'Story':
                issues.append({
                'key': issue['key'],
                'title': issue['fields']['summary'],
                })

        return issues

    except Exception as e:
        raise e



def get_issue_by_id(issue_key):
    try:
        base_url = JIRA_SERVER
        url = f'{base_url}/rest/api/3/issue/{issue_key}'
        headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers, auth=AUTH)
        response.raise_for_status() 
        
        # print(response.json())
        with open('data.json', 'w') as json_file:
            json.dump(response.json(), json_file, indent=4)

        return response.json()
    except requests.exceptions.RequestException as error:
        print('error: ')
        print(error.response.json().get('errors'))



# print('get_userstories \n\n\n',get_userstories('RDKB'))
# print('\n\n\nget_issue_by_id \n\n\n',get_issue_by_id('RDKB-370'))


prompt = 'what is the name of rdkb-370?'
id=f'Extract the issue ID from the following prompt and return it in capital letters only: {prompt}'

from archive.llm_settings import LLM
# llm_instance = LLM(llm_model='llama3', debug_mode=True)
llm_instance = LLM(llm_model='llama3')
id = llm_instance.fetch_entire_response(id)

jira_content = get_issue_by_id('RDKB-370')
q = f'From {jira_content}, \n\n Answer this {prompt} Please provide the answer clearly.'
ans = llm_instance.fetch_entire_response(q)
print(ans)
