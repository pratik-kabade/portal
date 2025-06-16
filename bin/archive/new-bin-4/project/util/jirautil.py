import os
import requests
from jira import JIRA

# JIRA_SERVER = os.getenv('JIRA_SERVER')
# JIRA_USERNAME = os.getenv('JIRA_USERNAME')
# JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_SERVER='https://testingjirainsandbox.atlassian.net'
JIRA_USERNAME='thisispratikkabade@gmail.com'
JIRA_API_TOKEN='ATATT3xFfGF0qwdVeuZjX2c0s5jwJXhMViYVfhLwiqEDnIzyTlHyciFxdWe9rZE9IOZm6cWrW89t-SwfGQL8EH2-Zj9O18-VqtnVPyiUlTB4jGb__fxq9_mEqZhb0dt9jys65PKGBE3xyK7KP1vv846mKel6UCjrnLJ67M3HpQNJ-OmbbFpNJJc=21D979B4'

PROJECT_KEY = "RDKB"
AUTH = (JIRA_USERNAME, JIRA_API_TOKEN)

def createNewissue(_summary, _description, _issuetype):
    try:
        # Summary and Description for the new issue
        summary = str(_summary)
        description = str(_description)

        # Creating a JIRA connection
        options = { 'server': JIRA_SERVER,
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

        # Link the issue with Parent
        jira.create_issue_link(linktype, parentkey, new_issue.key)

        return_url = JIRA_SERVER + "/browse/" + new_issue.key
        return return_url

    except Exception as e:
        raise e

def status_transition(issue,status_id):
    try:
       # Creating a JIRA connection
       options = { 'server': JIRA_SERVER,
                'verify': True
       }

       # Creating a JIRA connection
       jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

       # Change the status
       statusId = jira.transition_issue(issue, status_id)
       return True

    except Exception as e:
        raise e

def get_issue_status(issue_key):
    try:
       # Creating a JIRA connection
       options = { 'server': JIRA_SERVER,
                  'verify': True
      }

       # Creating a JIRA connection
       jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
       issue = jira.issue(issue_key)
       issue_status = issue.fields.status.name
       return issue_status

    except Exception as e:
        raise e

def create_newissue(_summary, _description, userstory, teststeps):

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
            customfield_10036=userstory,
            customfield_10037="TESTING STEPS",
            issuetype={'name': 'Task'})

       return_url = JIRA_SERVER + "/browse/" + new_issue.key
       return return_url
    except Exception as e:
       raise e

def create_newuserstory(_summary, _description):

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
       new_issue = jira.create_issue(project=PROJECT_KEY, \
            summary=summary,
            description=description,
            issuetype={'name': 'Story'})

       return new_issue.key

    except Exception as e:
       raise e


def create_newbug(_summary, _description):

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
       new_bug = jira.create_issue(project=PROJECT_KEY, \
                                   summary=summary,
                                   description=description,
                                   issuetype={'name': 'Bug'})

       return_url = JIRA_SERVER + "/browse/" + new_bug.key
       return return_url

    except Exception as e:
       raise e

def update_jira_ticket(issuekey):
    try:
        options = {
          'server': JIRA_SERVER,
          'verify': True
        }
        jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
        issue = jira.issue(issuekey)
        transitions = jira.transitions(issue)

        # Find the transition to the "Failed" status
        failed_transition = next(t for t in transitions if t['name'] == 'Failed')
        jira.transition_issue(issue, failed_transition['id'])

        transitions = jira.transitions(issue)
        print('tttttttttttttt-',transitions)

    except Exception as e:
      print(f"Error updating Jira issue: {e}")

def updateJira(issuekey,teststeps):
    # Creating a JIRA connection

    try:
        options = {
          'server': JIRA_SERVER,
          'verify': True
        }
        jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

        # Get the issue object
        issue = jira.issue(issuekey)
        fields_to_update = {
           "description": teststeps
	}
        # Update the issue fields
        issue.update(fields=fields_to_update)
        return True
    except Exception as e:
        raise e

def create_child_issue(parent_issue_key, userstory, testscripts):

    try:
        options = {
         'server': JIRA_SERVER,
         'verify': True
        }

        jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

        # Create the child issue
        new_issue = jira.create_issue(project=PROJECT_KEY, \
            summary=userstory, 
            description=testscripts,
            issuetype={'name': 'Sub-task'},
            parent={'key': parent_issue_key})

        #print (f"issue created",new_issue)
        return JIRA_SERVER + "/browse/" + new_issue.key
    except Exception as e:
        raise e

def updateChildJira(issuekey,testscript):
    # Creating a JIRA connection

    try:
        options = {
          'server': JIRA_SERVER,
          'verify': True
        }
        jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

        # Get the issue object
        issue = jira.issue(issuekey)
        fields_to_update = {
           "description": testscript
        }
        # Update the issue fields
        issue.update(fields=fields_to_update)
        return True
    except Exception as e:
        raise e


def get_projects():
    try:
        base_url = JIRA_SERVER
        url = f'{base_url}/rest/api/3/project/recent'
        headers = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers, auth=AUTH)
        response.raise_for_status()
        projects = []

        for project in response.json():
            projects.append({
               'id': project.get('id'),
               'key': project.get('key'),
               'name': project.get('name'),
                })

        return projects
    except requests.RequestException as error:
        print('error: /n' + error.message)
        return error.message


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

def getBugsStatus(projects):
   options = {
                 'server': JIRA_SERVER,
                 'verify': True
             }

   jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
   result = []

   for project in projects:
       pass_bugs = []
       done_bugs = []
       project_key = project['jiraprojectKey']

       jql_query = f'project = {project_key} AND issuetype = Bug'
       print("after jql")
       issues = jira.search_issues(jql_query, maxResults=100)

       for issue in issues:
           if (issue.fields.status.name == 'Done'):
               pass_bugs.append(issue)
           elif (issue.fields.status.name == 'PASSED'):
               done_bugs.append(issue)


       result.append({
                        "name": project['title'],
                        "pass": len(pass_bugs),
                        "done": len(done_bugs),
                        "not executed": len(issues) - len(pass_bugs) - len(done_bugs)
                    })

   return result






















