import os
import base64
import requests
from jira import JIRA


# JIRA server authentication
JIRA_SERVER = "https://testingjirainsandbox.atlassian.net"
JIRA_USERNAME = "anurag.agr@gmail.com"
JIRA_API_TOKEN ='ATATT3xFfGF0oDQxIXShOZuI-rziZ8oAyvnQU1HoBXNfWqZbC2qPHRpNTBoA23zJzuehn6fkFmGOuqXDQqT28K1bj02g3DVIl5sQ8WMePeULGDx0ObDoRf3mrtnD5fhGRJruShf3cQejmQxFE-oA0hR0UnxOZVJAkEpVkC-Xkk_UAFhcMTPS2Wg=40528401'
PROJECT_KEY = "RDKB"
AUTH = (JIRA_USERNAME, JIRA_API_TOKEN)

def fetch_bug_data(issue_key):
  url = f"{JIRA_SERVER}/rest/api/3/issue/{issue_key}"
  #auth_string = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
  #encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
  headers = {'Content-Type': 'application/json'}
  response = requests.get(url, headers=headers, auth=AUTH)
  if response.status_code == 200:
     print(response.json())

fetch_bug_data("RDKB-171")

