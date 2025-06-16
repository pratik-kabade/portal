import os
from jira import JIRA

# Project key where you want to create the issue

# JIRA server authentication
JIRA_SERVER = "https://testingjirainsandbox.atlassian.net"
JIRA_USERNAME = "anurag.agr@gmail.com"
JIRA_API_TOKEN = 'ATATT3xFfGF0oDQxIXShOZuI-rziZ8oAyvnQU1HoBXNfWqZbC2qPHRpNTBoA23zJzuehn6fkFmGOuqXDQqT28K1bj02g3DVIl5sQ8WMePeULGDx0ObDoRf3mrtnD5fhGRJruShf3cQejmQxFE-oA0hR0UnxOZVJAkEpVkC-Xkk_UAFhcMTPS2Wg=40528401'
PROJECT_KEY = "RDKB"

def createNewissue(_summary, _description, _issuetype):
    try:
        print("create_newissue")
        # Summary and Description for the new issue
        summary = str(_summary)
        description = str(_description)

        # Creating a JIRA connection
        options = {
            'server': JIRA_SERVER,
            'verify': True
        }

        # Creating a JIRA connection
        jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
        # Create the issue
        new_issue = jira.create_issue(project=PROJECT_KEY, \
                                      summary=summary,
                                      description=description,
                                      issuetype={'name': _issuetype })

        return_url = JIRA_SERVER + "/browse/" + new_issue.key
        return return_url
    except Exception as e:
        print(e)
        raise e

def createNewIssueAndLink(_summary, _description, _issuetype, parentkey, linktype):
     try:
         print("create_newissue")
         # Summary and Description for the new issue
         summary = str(_summary)
         description = str(_description)

         # Creating a JIRA connection
         options = {
                 'server': JIRA_SERVER,
                 'verify': True
                 }

         # Creating a JIRA connection
         jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
         # Create the issue
         new_issue = jira.create_issue(project=PROJECT_KEY, \
                 summary=summary,
                 description=description,
                 issuetype={'name': _issuetype })
         print (f"new issue = " +new_issue.key)

         jira.create_issue_link(linktype, parentkey, new_issue.key)

         return_url = JIRA_SERVER + "/browse/" + new_issue.key
         return return_url
         except Exception as e:
             print(e)
             raise e

url = create_newissue("a","b","TestScript")

print(url)
