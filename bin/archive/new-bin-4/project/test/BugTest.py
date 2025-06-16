import requests
import json
import os
from jira import JIRA



jira_url = "https://testingjirainsandbox.atlassian.net"
JIRA_USERNAME = "anurag.agr@gmail.com"
JIRA_API_TOKEN ='ATATT3xFfGF0oDQxIXShOZuI-rziZ8oAyvnQU1HoBXNfWqZbC2qPHRpNTBoA23zJzuehn6fkFmGOuqXDQqT28K1bj02g3DVIl5sQ8WMePeULGDx0ObDoR0ObDoRf3mrtnD5fhGRJruShf3cQejmQxFE-oA0hR0UnxOZVJAkEpVkC-Xkk_UAFhcMTPS2Wg=40528401'
AUTH = (JIRA_USERNAME, JIRA_API_TOKEN)
project_key= "RDKB"


def fetch_bug_counts(jira_url, AUTH, project_key):

    headers= {'Content-Type': 'application/json'}
    jql_open = f"project = {project_key} AND issuetype = Bug AND status != Closed"
    jql_closed = f"project = {project_key} AND issuetype = Bug AND status = Closed"

    def get_issue_count(jql):
      params = {'jql': jql}
      response = requests.get(jira_url + '/rest/api/3/search', headers=headers, params=params, auth=AUTH)
      if response.status_code == 200:
        data = json.loads(response.text)
        return data['total']
      else:
        print(f"Error fetching data: {response.status_code}")
        return None

    open_bugs = get_issue_count(jql_open)
    closed_bugs = get_issue_count(jql_closed)

    return {'open': open_bugs, 'closed': closed_bugs}


bug_counts = fetch_bug_counts(jira_url, AUTH, project_key)
print(bug_counts)
