import requests
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import json
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, load_index_from_storage, StorageContext
from llama_parse import LlamaParse
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-TuxnaMbo4c7TYeo9EjxpZX4oPMxEDAsX4a8AuxogvurFbklO"
# Load environment variables
load_dotenv()

ATLASSIAN_USERNAME='thisispratikkabade@gmail.com'
ATLASSIAN_API_KEY='ATATT3xFfGF0qwdVeuZjX2c0s5jwJXhMViYVfhLwiqEDnIzyTlHyciFxdWe9rZE9IOZm6cWrW89t-SwfGQL8EH2-Zj9O18-VqtnVPyiUlTB4jGb__fxq9_mEqZhb0dt9jys65PKGBE3xyK7KP1vv846mKel6UCjrnLJ67M3HpQNJ-OmbbFpNJJc=21D979B4'
LEAD_ACCT_ID='640dffb3af3b93d8ecf0db6a'
DOMAIN='testingjirainsandbox'
PROJECT_KEY='RDKB'
PROJECT_NAME='TestProject22'

class JiraSetting:
    def __init__(
            self,
            username = ATLASSIAN_USERNAME,
            password = ATLASSIAN_API_KEY,
            domain = DOMAIN,
            lead_account_id = LEAD_ACCT_ID,
            project_key = PROJECT_NAME
            ):
        self.username = username 
        self.password = password 
        self.domain = domain 
        self.lead_account_id = lead_account_id 
        self.project_key = project_key 

        self.auth = HTTPBasicAuth(self.username, self.password)

    # Gets comments of an issue by its ID using the Jira Cloud REST API
    def get_comments_by_id(self, issue_key):
        try:
            base_url = f'https://{self.domain}.atlassian.net'
            url = f'{base_url}/rest/api/3/issue/{issue_key}'
            headers = {'Content-Type': 'application/json'}
            response = requests.get(url, headers=headers, auth=self.auth)
            response.raise_for_status() 

            issue_details = response.json()
            comments = issue_details.get('fields', {}).get('comment', {}).get('comments', [])

            filtered_details = [
                comment.get('body', {}).get('content', [])[0].get('content', [])[0].get('text', '')
                for comment in comments
            ]
            return filtered_details
        except requests.exceptions.RequestException as error:
            print('error: ')
            print(error.response.json().get('errors'))

    # Gets all issues in a particular project using the Jira Cloud REST API
    def get_issues(self):
        try:
            base_url = f'https://{self.domain}.atlassian.net'
            url = f'{base_url}/rest/api/3/search/?fields=issue,summary,description,status,labels,comments,issuelinks&jql=project=RDKB'
            headers = {'Content-Type': 'application/json'}
            start_at = 0
            all_issues = []  # This will accumulate all issues

            # Initial request to get the total number of issues
            response = requests.get(url, headers=headers, auth=self.auth)
            response.raise_for_status()
            total = response.json().get('total')
            print(total)
            while start_at < total:
                params = {
                    "startAt": start_at,
                    "maxResults": total,
                }

                response = requests.get(url, headers=headers, auth=self.auth, params=params)
                response.raise_for_status()

                issues = response.json().get('issues', [])
                print(len(issues))
                all_issues.extend(issues)
                start_at += 100
            filtered_issues = []
            idx=0
            for issue in all_issues:
                #if issue.get('key').split('-')[0] == "RDKB":
                a = {
                    'key': issue.get('key'),
                    'summary': issue.get('fields', {}).get('summary'),
                    'description': (
                        issue.get('fields', {}).get('description', {}).get('content', [{}])[0].get('content', [{}])[0].get('text')
                        if issue.get('fields', {}).get('description') else None
                    ),
                    'status': issue.get('fields', {}).get('status', {}).get('name'),
                    'labels': issue.get('fields', {}).get('labels'),
                    'comments': self.get_comments_by_id(issue.get('key')),
                    'issuelinks': (
                        issue.get('fields', {}).get('issuelinks', [{}])[0].get('inwardIssue', {}).get('key', '')
                        if issue.get('fields', {}).get('issuelinks') else None
                    ),
                    }
                filtered_issues.append(a)
                idx+=1
                if idx%10 == 0:
                    print(idx)
                    json_string = json.dumps(filtered_issues)
                    json_value = json.loads(json_string)
                    with open('db/'+str(idx)+'.txt', 'w') as file:
                        json.dump(json_value, file, indent=4)
                    filtered_issues=[]

                #for issue in all_issues  # Process all accumulated issues
            #]
            '''
            filtered_issues2 = []
            for i in filtered_issues:
                a=i.get('key').split('-')[0]
                if a=='RDKB':
                    filtered_issues2.append(i)
            '''
            print(len(filtered_issues))
            return filtered_issues

        except requests.exceptions.RequestException as error:
            print('error: ')
            print(error.response.json().get('errors'))

def rag_model(prompt):
    
    file_path = f"./issues.pdf"
    persist_dir = f"./RDK-B"

    Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
    Settings.llm = Ollama(model='llama3:latest', request_timeout=120.0, temperature=0)

    documents = LlamaParse(result_type="text").load_data(file_path)
    print(documents)
    if not os.path.exists(os.path.join(persist_dir, "default__vector_store.json")):
        print('Creating indexes..')
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=persist_dir)
    else:
        print('Loading indexes..')
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context=storage_context)

    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)
    print(response)



if __name__ == "__main__":
    
    # jira = JiraSetting()
    # issues = jira.get_issues()
    # json_string = json.dumps(issues)

    # json_value = json.loads(json_string)
    # with open('db/rest.txt', 'w') as file:
    #     json.dump(json_value, file, indent=4)
    # print('done!')

    print(os.listdir('db'))
    
    # rag_model("What is the summary of issue with key RDKB-276?")


