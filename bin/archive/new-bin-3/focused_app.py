# project/do/testmgmt.py
asktestcases_api = Blueprint('asktestcases_api', __name__)
@asktestcases_api.route('/api/ask/tm/testcases', methods=['POST'])
def ask_testcases():

    # NOTE:DB-GET (projectname)
    request.json['question']
    request.json['user']
    request.json['project']
    request.json['userstory_id']

    # NOTE:JIRA-CREATE
    # NOTE:DB-CREATE
    mainPrompt = "[INST]\n" + myprompts.TC_PERSONA + "\n\n" + myprompts.TC_FORMAT + "\n[/INST]\n" + "<<<USERSTORY>>>\n" + question

    # # # NOTE:LLM

    # NOTE:DB-CREATE




asktestscripts_api = Blueprint('asktestscripts_api', __name__)
@asktestscripts_api.route('/api/ask/tm/testscripts', methods=['POST'])
def ask_testscripts():
    request.json['question']
    request.json['language']
    request.json['tc_id']
    request.json['project']

    testcase = "\n<<<test case>>> \n " + question
    tc_language = "\n<<<language>>> " + language

    # NOTE:DB-GET
    mainPrompt = "[INST]\n" + myprompts.TS_PERSONA + "\n\n" + myprompts.TS_FORMAT + testcase + tc_language

    # # # NOTE:LLM

    # NOTE:DB-CREATE





testscriptoutput_api = Blueprint('testscriptoutputapi', __name__)
@testscriptoutput_api.route('/api/tsoutput/<user>', methods=['POST'])
def testscriptOutput(user):
    request.json['testcase']
    request.json['script_content']
    request.json['output']
    request.json['project']
    request.json['tc_jira']

    # NOTE:DB-GET(projectname)
    mainPrompt = myprompts.RCA_PERSONA + " \n <<<TESTCASE>>> \n " + testcase + "\n  <<<TESTSCRIPT>>> \n " + testscript_content + myprompts.RCA_FORMAT + "\n <<<OUTPUT>>> \n" + output 

    # # # NOTE:LLM

    # NOTE:DB-GET(rca)

    # NOTE:DB-CREATE
