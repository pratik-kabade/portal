import requests
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import json

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
            url = f'{base_url}/rest/api/3/search'
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
                all_issues.extend(issues) 
                start_at += 100
                
            filtered_issues = [
                {
                    'key': issue.get('key'),
                    'summary': issue.get('fields', {}).get('summary'),
                    'description': (
                        issue.get('fields', {}).get('description', {}).get('content', [{}])[0].get('content', [{}])[0].get('text')
                        if issue.get('fields', {}).get('description') else None
                    ),
                    'status': issue.get('fields', {}).get('status', {}).get('name'),
                    'labels': issue.get('fields', {}).get('labels'),
                    # 'comments': self.get_comments_by_id(issue.get('key')),
                    'issuelinks': (
                        issue.get('fields', {}).get('issuelinks', [{}])[0].get('inwardIssue', {}).get('key', '')
                        if issue.get('fields', {}).get('issuelinks') else None
                    ),
                }
                for issue in all_issues  # Process all accumulated issues
            ]
            
            filtered_issues2 = []
            for i in filtered_issues:
                a=i.get('key').split('-')[0]
                if a=='RDKB':
                    filtered_issues2.append(i)
            
            return filtered_issues2
        except requests.exceptions.RequestException as error:
            print('error: ')
            print(error.response.json().get('errors'))


if __name__ == "__main__":
    jira = JiraSetting()
    issues = jira.get_issues()
    json_string = json.dumps(issues)

    json_value = json.loads(json_string)
    with open('issues_all.json', 'w') as file:
        json.dump(json_value, file, indent=4)
    print('done!')

