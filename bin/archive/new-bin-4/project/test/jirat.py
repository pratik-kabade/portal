import os
from jira import JIRA

# JIRA server authentication
JIRA_SERVER = "https://testingjirainsandbox.atlassian.net"
JIRA_USERNAME = "anurag.agr@gmail.com"
JIRA_API_TOKEN = 'ATATT3xFfGF0oDQxIXShOZuI-rziZ8oAyvnQU1HoBXNfWqZbC2qPHRpNTBoA23zJzuehn6fkFmGOuqXDQqT28K1bj02g3DVIl5sQ8WMePeULGDx0ObDoRf3mrtnD5fhGRJruShf3cQejmQxFE-oA0hR0UnxOZVJAkEpVkC-Xkk_UAFhcMTPS2Wg=40528401'
PROJECT_KEY = "RDKB"

def createNewissue(_summary, _description, _issuetype):
    try:

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
        print(new_issue)
        print(new_issue.fields.status.name)
        print(new_issue.fields.status.id)

        t = jira.transitions(new_issue)
        print(t)
        #for tran in t:
         #   print (f"ID={tran['id']} --name- {tran['name']}")
          #  inprogressid = tran['id']

       # print (f"next id = ", inprogres)
       # jira.transition_issue(new_issue, '6')
       # jira.transition_issue(new_issue, '2')
       # print(f"new id = ", new_issue.fields.status.id)
       # t = jira.transitions(new_issue)
       # for tran in t:
        #    print (f"ID={tran['id']} --name- {tran['name']}")

        return_url = JIRA_SERVER + "/browse/" + new_issue.key
        return return_url
    except Exception as e:
        print(e)
        raise e

def changeStatus(issuekey, statusId):
    print("#######################", statusId, issuekey, "##############################")
    options = {
              'server': JIRA_SERVER,
              'verify': True
              }

    jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
    t = jira.transitions(issuekey)
    print(t)
    #jira.transition_issue(issuekey, '6')
    jira.transition_issue(issuekey, statusId)
    t = jira.transitions(issuekey)
    print(t)

    return True


def get_issue_status(issue_key):
    options = {
             'server': JIRA_SERVER,
             'verify': True
              }
    jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
    issue = jira.issue(issue_key)
    issue_status = issue.fields.status.name
    id = issue.fields.status.id
    print(issue_status)
    print(id)

def get_issue_status_id(issue_key):
    options = {
            'server': JIRA_SERVER,
             'verify': True
              }
    jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
    t = jira.transitions(issue_key)
    print(t)

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

#url = createNewissue("a","b","TestScript")
#get_issue_status("RDKB-72")
#get_issue_status_id("RDKB-153")
#changeStatus("RDKB-104", "4")
#changeStatus("RDKB-221","6") 
#changeStatus("RDKB-221","2") 
#changeStatus("RDKB-221","5")
changeStatus("RDKB-113","3")
#print(y)
