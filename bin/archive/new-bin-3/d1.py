import os
import json
import random
from datetime import datetime
from flask import Blueprint, Flask, request, jsonify
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.embeddings import resolve_embed_model
from util.genesislogger import GenesisLogger
from llm import LlamaIndexManager
from util import jirautil, testtojson
from db import DBUtil
from rest.prompts import myprompts

# Initialize Flask
app = Flask(__name__)

# Configure Logger
logger = GenesisLogger.get_instance()

# Set environment variables
db = os.getenv("MONGODB_NAME")
collection = "testcases"

# Define larger tools to handle comprehensive tasks

def handle_testcases_request(question: str, createdBy: str, projectID: str, userstory_id: str):
    """Handle the entire process of processing test cases."""
    logger.debug("Handling test cases request")

    # Fetch project details
    result = DBUtil.getDocumentByKeyValue(db, "projects", "_id", projectID)
    projectname = result[0]['title']

    # Check if data directory exists for the project
    DIR = os.path.join("data/", projectname)
    files = len(os.listdir(DIR))
    if files == 1:
        return [{'tc_id': '0', 'testcase': 'Please upload the document before querying'}]

    # Create new Jira issue if necessary
    new_userstory = jirautil.createNewissue(question, question, "Story")
    if userstory_id == "":
        record = {
            "_id": str(random.randint(1, 100000)),
            "project": projectID,
            "projectname": projectname,
            "jiraid": new_userstory.split('browse/')[1],
            "title": question,
            "createdby": createdBy,
            "createddate": str(datetime.utcnow())
        }
        userstory_id = DBUtil.createOrUpdate(db, "userstories", record)

    # Query the LLM to generate test cases
    mainPrompt = "[INST]\n" + myprompts.TC_PERSONA + "\n\n" + myprompts.TC_FORMAT + "\n[/INST]\n" + "<<<USERSTORY>>>\n" + question
    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
    queryengine = instance.getQueryEngine(projectname)
    response = queryengine.query(mainPrompt)

    # Convert response to JSON and save to the database
    tc_result = testtojson.text_to_json(str(response))
    tc_json_data = json.loads(tc_result)
    resp = []

    for i, case in enumerate(tc_json_data):
        tc_record = {
            "_id": str(random.randint(1, 100000)),
            "project": projectID,
            "userstory": userstory_id,
            "jirauserstoryId": new_userstory.split('browse/')[1],
            "testcase": case,
            "tc_title": case.split("Preconditions:")[0],
            "tc_jira": "",
            "tc_jira_key": "",
            "ts_jira_key": "",
            "testscript": "",
            "ts_jira": "",
            "testScriptStatus": "Not Executed",
            "bug_id": "",
            "language": "",
            "createdby": createdBy,
            "createddate": str(datetime.utcnow()),
            "updatedate": ""
        }
        tc_id = DBUtil.createOrUpdate(db, "testcases", tc_record)
        resp.append({"tc_id": tc_id, "testcase": case})

    return json.loads(json_util.dumps(resp))

def handle_testscripts_request(question: str, language: str, tc_id: str, projectID: str):
    """Handle the entire process of generating test scripts."""
    logger.debug("Handling test scripts request")

    # Fetch project details
    result = DBUtil.getDocumentByKeyValue(db, "projects", "_id", projectID)
    projectname = result[0]['title']

    # Prepare prompt for LLM query
    testcase = "\n<<<test case>>> \n " + question
    tc_language = "\n<<<language>>> " + language
    mainPrompt = "[INST]\n" + myprompts.TS_PERSONA + "\n\n" + myprompts.TS_FORMAT + testcase + tc_language

    # Query the LLM to generate test scripts
    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
    queryengine = instance.getQueryEngine(projectname)
    response = queryengine.query(mainPrompt)

    # Save test script to the database
    tc_record_update = {
        "_id": tc_id,
        "testscript": str(response),
        "projectname": projectname,
        "ts_jira": "",
        "language": language,
        "updatedate": str(datetime.utcnow())
    }
    DBUtil.createOrUpdate(db, "testcases", tc_record_update)

    return {'answer': str(response)}

def handle_tsoutput_request(user: str, output: str, testscript_content: str, testcase: str, projectID: str, tc_jiraid: str):
    """Handle the entire process of generating test script output."""
    logger.debug("Handling test script output request")

    # Fetch project details
    result = DBUtil.getDocumentByKeyValue(db, "projects", "_id", projectID)
    projectname = result[0]['title']

    # Prepare prompt for LLM query
    mainPrompt = myprompts.RCA_PERSONA + " \n <<<TESTCASE>>> \n " + testcase + "\n  <<<TESTSCRIPT>>> \n " + testscript_content + myprompts.RCA_FORMAT + "\n <<<OUTPUT>>> \n" + output

    # Query the LLM for RCA output
    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
    queryengine = instance.getQueryEngine(projectname)
    response = queryengine.query(mainPrompt)

    # Save RCA output to the database
    filter = {"createdby": user, "tc_jira_key": tc_jiraid}
    rca = DBUtil.getDocumentByMultipleKeyValue(db, collection, filter)
    rca[0]["rcaOutput"] = str(response)
    DBUtil.createOrUpdate(db, collection, rca[0])

    return {'answer': str(response)}

# Wrap larger functions with FunctionTool
testcases_tool = FunctionTool.from_defaults(
    fn=handle_testcases_request,
    description="Handle the entire process of handling test case queries. Expects question, createdBy, projectID, and userstory_id as inputs."
)

testscripts_tool = FunctionTool.from_defaults(
    fn=handle_testscripts_request,
    description="Handle the entire process of generating test scripts. Expects question, language, tc_id, and projectID as inputs."
)

tsoutput_tool = FunctionTool.from_defaults(
    fn=handle_tsoutput_request,
    description="Handle the entire process of generating test script outputs. Expects user, output, testscript_content, testcase, projectID, and tc_jiraid as inputs."
)

# Configure LLM settings
Settings.llm = Ollama(model="llama3", request_timeout=60.0, temperature=0)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

# Create the agent with all tools
agent = ReActAgent.from_tools(
    tools=[testcases_tool, testscripts_tool, tsoutput_tool],
    llm=Settings.llm,
    verbose=True
)

# delegating the agent
asktestcases_api = Blueprint('asktestcases_api', __name__)
@asktestcases_api.route('/api/ask/tm/testcases', methods=['POST'])
def ask_testcases():
    data = request.json
    prompt = f"Handle test case request with question: {data['question']}, created by: {data['user']}, for project ID: {data['project']}, user story ID: {data['userstory_id']}."
    response = agent.chat(prompt)
    return jsonify(response), 200

asktestscripts_api = Blueprint('asktestscripts_api', __name__)
@asktestscripts_api.route('/api/ask/tm/testscripts', methods=['POST'])
def ask_testscripts():
    data = request.json
    prompt = f"Handle test script request with question: {data['question']}, language: {data['language']}, for test case ID: {data['tc_id']}, project ID: {data['project']}."
    response = agent.chat(prompt)
    return jsonify(response), 200

testscriptoutput_api = Blueprint('testscriptoutputapi', __name__)
@testscriptoutput_api.route('/api/tsoutput/<user>', methods=['POST'])
def testscriptOutput(user):
    data = request.json
    prompt = f"Handle test script output request for user: {user} with output: {data['output']}, script content: {data['script_content']}, test case: {data['testcase']}, project ID: {data['project']}, Jira key: {data['tc_jira']}."
    response = agent.chat(prompt)
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)
