# from util import jirautil
# from flask import jsonify

# def userstories(projectkey):
#     try:
#         issues = jirautil.get_userstories(projectkey)
#         return jsonify(issues)
#     except Exception as error:
#         return jsonify({'error': 'An error occurred fetching the issues.'}), 500


# import os
# import requests
# from jira import JIRA

# JIRA_SERVER='https://iotpegenai.atlassian.net'
# JIRA_USERNAME='anurag.agr@gmail.com'
# JIRA_API_TOKEN='ATATT3xFfGF0rnMzi2atAgf0Q2uB53QnEpqSQqVmlmvg-sNUP0SPJpfojx4K208Vn-mcN7w7sT1wq1Gxhuh76aN0z0RcKj8zkKjM6G0W4IIMnDS_5kSvUy7tr2L1MUTdj6CtJaiWskoZ0pej_YdYhySWyk7z39mCkNsGqxOCtGqxOCtbhAkfHX1_VXgeY=8EE448A4'


# PROJECT_KEY = "RDKB"
# AUTH = (JIRA_USERNAME, JIRA_API_TOKEN)

# def get_userstories(ProjectKey):
#     try:
#         url = f'{JIRA_SERVER}/rest/api/3/search?fields=issue,summary,issuetype&jql=project={ProjectKey}'
#         headers = {'Content-Type': 'application/json'}

#         response = requests.get(url, headers=headers, auth=AUTH)
#         response.raise_for_status()
#         issues = []

#         for issue in response.json().get('issues', []):
#             if issue['fields']['issuetype']['name'] == 'Story':
#                 issues.append({
#                 'key': issue['key'],
#                 'title': issue['fields']['summary'],
#                 })

#         return issues

#     except Exception as e:
#         raise e


# print(get_userstories('RDKB'))
