############################################################################################################## project/do/docloader.py
getfile_api = Blueprint('getfile_api', __name__)
@getfile_api.route('/api/files/<user>', methods=['GET'])
def get_files(user):
    # +++ NOTE:DB-GET
    pass

upload_api = Blueprint('upload_api', __name__)
@upload_api.route('/api/upload/<user>/<projectName>', methods=['POST'])
def upload_file(user,projectName):
    # +++ NOTE:DB-CREATE
    pass

download_api = Blueprint('download_api', __name__)
@download_api.route('/api/download/<user>/<projectName>/<filename>', methods=['GET'])
def download_file(user, projectName, filename):
    pass

ingest_api = Blueprint('ingest_api', __name__)
@ingest_api.route('/api/ingest/<user>/<projectName>/<fileName>', methods=['POST'])
def ingest_file(user, projectName, fileName):
    instance.run_ingest(fileName, projectName)
    # >>> NOTE:LLM
    # +++ NOTE:DB-GET
    # +++ NOTE:DB-CREATE
    pass









############################################################################################################## project/do/execution.py
executescript_api = Blueprint('executescriptapi', __name__)
@executescript_api.route('/api/execute/<user>', methods=['POST'])
def executeScript(user):
    request.json['project']
    request.json["script_content"]
    request.json['tc_jira']
    request.json['tc_issue']
    request.json['ts_jira_key']
    # +++ NOTE:DB-GET

def executeScriptRDK(script_content,tc_jira, tc_issue, user, ts_jira_key):
    # ... NOTE:JIRA-GET
    # ... NOTE:JIRA-TRANSITION
    # ... NOTE:JIRA-CREATE
    # +++ NOTE:DB-GET
    # +++ NOTE:DB-CREATE
    pass

def executeScriptCisco(script_content,tc_jira,tc_issue,user, ts_jira_key):
    # ... NOTE:JIRA-GET
    # ... NOTE:JIRA-TRANSITION
    # ... NOTE:JIRA-CREATE
    # +++ NOTE:DB-GET
    # +++ NOTE:DB-CREATE
    pass










############################################################################################################## project/do/jirasettings.py
getjirasettings_api = Blueprint('getjirasettings_api', __name__)
@getjirasettings_api.route('/api/settings/jira', methods=['GET'])
def getsettings_jira():
    # +++ NOTE:DB-GET
    pass

createjirasettings_api = Blueprint('createjirasettings_api', __name__)
@createjirasettings_api.route('/api/settings/jira', methods=['PUT'])
def createsettings_jira():
    # +++ NOTE:DB-CREATE
    pass

deletejirasettings_api = Blueprint('deletejirasettings_api', __name__)
@deletejirasettings_api.route('/api/settings/jira/<_id>', methods=['DELETE'])
def delsettings_jira(_id):
    # +++ NOTE:DB-DELETE
    pass

createjira_api = Blueprint('createjira_api', __name__)
@createjira_api.route('/api/jira/<user>', methods=['POST'])
def create_jira(user):
    # +++ NOTE:DB-GET(parentkey)
    request.json['summary']
    request.json['tc_id']
    # +++ NOTE:DB-CREATE

updatejira_api = Blueprint('updatejira_api', __name__)
@updatejira_api.route('/api/jira/<jiraid>', methods=['PUT'])
def update_jira(jiraid):
    request.json['tc_id']
    request.json['testcase']
    # +++ NOTE:DB-CREATE

create_child_jira_api = Blueprint('create_child_jira_api', __name__)
@create_child_jira_api.route('/api/jira/createchild', methods=['POST'])
def create_child_jira():
    request.json['parentkey']
    request.json['testcase_title']
    request.json['testscript']
    request.json['tc_id']
    # +++ NOTE:DB-CREATE

updatechildjira_api = Blueprint('updatechildjira_api', __name__)
@updatechildjira_api.route('/api/jira/updatechild', methods=['PUT'])
def updatechild_jira():
    request.json['jira_id']
    request.json['tc_id']
    request.json['testscript']
    # +++ NOTE:DB-CREATE

getjiraproject_api = Blueprint('getjiraproject_api', __name__)
@getjiraproject_api.route('/api/jira/projects/', methods=['GET'])
def projects():
    pass

getjirauserstories_api = Blueprint('getjirauserstories_api', __name__)
@getjirauserstories_api.route('/api/jira/userstory/<projectkey>', methods=['GET'])
def userstories(projectkey):
    pass








############################################################################################################## project/do/project.py
getproject_api = Blueprint('getproject_api', __name__)
@getproject_api.route('/api/projects/<user>', methods=['GET'])
def getProjects(user):
    # +++ NOTE:DB-GET
    pass

getProjectdata_api = Blueprint('getProjectdata_api', __name__)
@getProjectdata_api.route('/api/projects/<user>/<_id>', methods=['GET'])
def getProjectdata(user,_id):
    # +++ NOTE:DB-GET
    pass

createproject_api = Blueprint('createproject_api', __name__)
@createproject_api.route('/api/projects/<user>', methods=['POST'])
def createProject(user):
    request.json['title']
    request.json['description']
    request.json['jiraProjectKey']
    request.json['jiraProjectName']
    # +++ NOTE:DB-CREATE
    llama_index_manager.run_ingest(FNAME, projectName)
    # >>> NOTE:LLM
    # +++ NOTE:DB-CREATE TODO

deleteproject_api = Blueprint('deleteproject_api', __name__)
@deleteproject_api.route('/api/projects/<user>/<_id>', methods=['DELETE'])
def deleteProject(user, _id):
    # +++ NOTE:DB-DELETE
    pass












############################################################################################################## project/do/test_bed.py
set_testbed_api = Blueprint('set_testbed_api', __name__)
@set_testbed_api.route('/api/testbed/<user>', methods=['POST'])
def testBed(user):
    data.get("name", "")
    data.get("description", "")
    data.get("port", "")
    data.get("hostname", "")
    data.get("username", "")
    data.get("password", "")
    data.get("devicetype", "")
    # +++ NOTE:DB-CREATE

update_testbed_api = Blueprint('update_testbed_api', __name__)
@update_testbed_api.route('/api/testbed/<user>/<id>', methods=['PUT'])
def updateTestBed(user, id):
    data.get("name", "")
    data.get("description", "")
    data.get("port", "")
    data.get("hostname", "")
    data.get("username", "")
    data.get("password", "")
    data.get("devicetype", "")
    # +++ NOTE:DB-CREATE

get_testbed_api = Blueprint('get_testbed_api', __name__)
@get_testbed_api.route('/api/testbed/<user>', methods=['GET'])
def getTestBed(user):
    # +++ NOTE:DB-GET
    pass

delete_testbed_api = Blueprint('delete_testbed_api', __name__)
@delete_testbed_api.route('/api/testbed/<user>/<id>', methods=['DELETE'])
def deleteTestBed(user, id):
    # +++ NOTE:DB-DELETE
    pass








############################################################################################################## project/do/testcases.py
gettestcases_api = Blueprint('gettestcases_api', __name__)
@gettestcases_api.route('/api/testcases/<user>/<_id>', methods=['GET'])
def getTestCases(user,_id):
    # +++ NOTE:DB-GET
    pass

getmultipletestcases_api = Blueprint('getmultipletestcases_api', __name__)
@getmultipletestcases_api.route('/api/testcases/<user>', methods=['POST'])
def getmultipletestcases(user):
    # +++ NOTE:DB-GET
    pass

getProjectData_api = Blueprint('getProjectData_api', __name__)
@getProjectData_api.route('/api/projectData/<user>', methods=['POST'])
def getProjectData(user):
    # +++ NOTE:DB-GET
    pass








############################################################################################################## project/do/testmgmt.py
asktestcases_api = Blueprint('asktestcases_api', __name__)
@asktestcases_api.route('/api/ask/tm/testcases', methods=['POST'])
def ask_testcases():
    # +++ NOTE:DB-GET (projectname)
    request.json['question']
    request.json['user']
    request.json['project']
    request.json['userstory_id']
    # ... NOTE:JIRA-CREATE
    # +++ NOTE:DB-CREATE
    mainPrompt = "[INST]\n" + myprompts.TC_PERSONA + "\n\n" + myprompts.TC_FORMAT + "\n[/INST]\n" + "<<<USERSTORY>>>\n" + question
    # >>> NOTE:LLM
    # +++ NOTE:DB-CREATE

asktestscripts_api = Blueprint('asktestscripts_api', __name__)
@asktestscripts_api.route('/api/ask/tm/testscripts', methods=['POST'])
def ask_testscripts():
    request.json['question']
    request.json['language']
    request.json['tc_id']
    request.json['project']
    # +++ NOTE:DB-GET
    mainPrompt = "[INST]\n" + myprompts.TS_PERSONA + "\n\n" + myprompts.TS_FORMAT + testcase + tc_language
    # >>> NOTE:LLM
    # +++ NOTE:DB-CREATE

testscriptoutput_api = Blueprint('testscriptoutputapi', __name__)
@testscriptoutput_api.route('/api/tsoutput/<user>', methods=['POST'])
def testscriptOutput(user):
    request.json['output']
    request.json['script_content']
    request.json['testcase']
    request.json['project']
    request.json['tc_jira']
    # +++ NOTE:DB-GET(projectname)
    mainPrompt = myprompts.RCA_PERSONA + " \n <<<TESTCASE>>> \n " + testcase + "\n  <<<TESTSCRIPT>>> \n " + testscript_content + myprompts.RCA_FORMAT + "\n <<<OUTPUT>>> \n" + output 
    # >>> NOTE:LLM
    # +++ NOTE:DB-GET(rca)
    # +++ NOTE:DB-CREATE









getuserstory_api = Blueprint('getuserstory_api', __name__)
@getuserstory_api.route('/api/userstory/<user>', methods=['GET'])
def getUserStory(user):
    # +++ NOTE:DB-GET
    pass

getuserstory_prj_api = Blueprint('getuserstory_prj_api', __name__)
@getuserstory_prj_api.route('/api/userstory/<prj>/<user>', methods=['GET'])
def getUserStoryForProject(prj,user):
    # +++ NOTE:DB-GET
    pass

createuserstory_api = Blueprint('createuserstory_api', __name__)
@createuserstory_api.route('/api/userstory/<user>', methods=['POST'])
def createUserStory(user):
    # +++ NOTE:DB-GET
    # +++ NOTE:DB-CREATE
    pass

deleteuserstory_api = Blueprint('deleteuserstory_api', __name__)
@deleteuserstory_api.route('/api/userstory/<user>/<usid>', methods=['DELETE'])
def deleteUserStory(user, usid):
    # +++ NOTE:DB-DELETE
    pass

delete_tc_in_us_api = Blueprint('delete_tc_in_us_api', __name__)
@delete_tc_in_us_api.route('/api/userstory/tc/<user>/<tcid>', methods=['DELETE'])
def deleteTCInUserStory(user, tcid):
    # +++ NOTE:DB-DELETE
    pass
