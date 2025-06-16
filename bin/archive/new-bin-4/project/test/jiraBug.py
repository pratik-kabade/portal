from jira import JIRA
from flask import jsonify

JIRA_SERVER = "https://testingjirainsandbox.atlassian.net"
JIRA_USERNAME = "anurag.agr@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0oDQxIXShOZuI-rziZ8oAyvnQU1HoBXNfWqZbC2qPHRpNTBoA23zJzuehn6fkFmGOuqXDQqT28K1bj02g3DVIl5sQ8WMePeULGDx0ObDoRf3mrtnD5fhGRJruShf3cQejmQxFE-oA0hR0UnxOZVJAkEpVkC-Xkk_UAFhcMTPS2Wg=40528401" 
basic_auth = (JIRA_USERNAME, JIRA_API_TOKEN)
project_key= "RDKB"

def fetch_bugs_from_projects(project_key):

    options = { 'server': JIRA_SERVER,
                'verify': True
              }

    jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

    passBugs = []
    doneBugs = []

    jql_query = f'project = {project_key} AND issuetype = Bug'
    issues = jira.search_issues(jql_query, maxResults=100)

    for issue in issues:
        print(issue.fields.status)
        if (issue.fields.status.name == 'Done'):
            passBugs.append(issue)
        elif (issue.fields.status.name == 'PASSED'):
            doneBugs.append(issue)

    print(len(issues), len(passBugs), len(doneBugs))
    return

fetch_bugs_from_projects(project_key)
