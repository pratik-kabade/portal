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

# Define utility functions
def create_jira_issue(summary: str, description: str, issuetype: str):
    return jirautil.createNewissue(summary, description, issuetype)

def get_document_by_key_value(db_name: str, collection_name: str, key: str, value):
    return DBUtil.getDocumentByKeyValue(db_name, collection_name, key, value)

def create_or_update_document(db_name: str, collection_name: str, document):
    return DBUtil.createOrUpdate(db_name, collection_name, document)

def get_query_engine(projectname: str):
    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
    return instance.getQueryEngine(projectname)

# Wrap functions with FunctionTool
create_issue_tool = FunctionTool.from_defaults(
    fn=create_jira_issue,
    description="Create a new issue in Jira. Expects a summary, description, and issue type."
)

get_document_tool = FunctionTool.from_defaults(
    fn=get_document_by_key_value,
    description="Fetch documents from the database based on key-value pairs."
)

create_or_update_tool = FunctionTool.from_defaults(
    fn=create_or_update_document,
    description="Create or update a document in the database."
)

get_query_engine_tool = FunctionTool.from_defaults(
    fn=get_query_engine,
    description="Get the query engine for a given project."
)

# Configure LLM settings
Settings.llm = Ollama(model="llama3", request_timeout=60.0, temperature=0)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

# Create the agent with all tools
agent = ReActAgent.from_tools(
    tools=[create_issue_tool, get_document_tool, create_or_update_tool, get_query_engine_tool],  
    llm=Settings.llm,
    verbose=True 
)



















asktestcases_api = Blueprint('asktestcases_api', __name__)
@asktestcases_api.route('/api/ask/tm/testcases', methods=['POST'])
def ask_testcases():
    logger.debug("In asktestcases_api")

    question = request.json['question']
    createdBy = request.json['user']
    projectID = request.json['project']
    userstory_id = request.json['userstory_id']

    prompt_fetch_project = f"Fetch project details for project ID '{projectID}' from the database."
    result = agent.chat(prompt_fetch_project)

    projectname = result[0]['title']
    DIR = os.path.join("data/", projectname)
    files = len(os.listdir(DIR))
    STD_OUTPUT = [{'tc_id': '0', 'testcase': 'Please upload the document before querying'}]
    if files == 1:
        return jsonify(STD_OUTPUT)

    # Create new Jira issue
    prompt_create_issue = f"Create a new Jira issue with the summary '{question}', description '{question}', and issue type 'Story'."
    new_userstory = agent.chat(prompt_create_issue)

    # Check userstory_id and handle accordingly
    if userstory_id == "":
        prompt_create_record = f"Create or update a user story record in the database with project ID '{projectID}', project name '{projectname}', Jira ID '{new_userstory.split('browse/')[1]}', title '{question}', and created by '{createdBy}'."
        userstory_id = agent.chat(prompt_create_record)

    # PROMPT
    mainPrompt = "[INST]\n" + myprompts.TC_PERSONA + "\n\n" + myprompts.TC_FORMAT + "\n[/INST]\n" + "<<<USERSTORY>>>\n" + question
    prompt_query_engine = f"Query the test case generation engine for project '{projectname}' with the prompt: {mainPrompt}."
    response = agent.chat(prompt_query_engine)

    # JSON
    tc_result = testtojson.text_to_json(str(response))
    tc_json_data = json.loads(tc_result)
    resp = []

    # database
    for i, case in enumerate(tc_json_data):
        tc_record = {
            "_id": str(random.randint(1, 100000)),
            "project": projectID,
            "userstory": userstory_id,
            "jirauserstoryId": new_userstory.split('browse/')[1],
            "testcase": case,
            "tc_title": case.split("Preconditions:")[0],
            "createdby": createdBy,
            "createddate": str(datetime.utcnow())
        }
        prompt_save_testcase = f"Create or update a test case record in the database for project '{projectID}' with data: {tc_record}."
        tc_id = agent.chat(prompt_save_testcase)
        resp.append({"tc_id": tc_id, "testcase": case})

    return jsonify(json.loads(json.dumps(resp)))


asktestscripts_api = Blueprint('asktestscripts_api', __name__)
@asktestscripts_api.route('/api/ask/tm/testscripts', methods=['POST'])
def ask_testscripts():
    logger.debug("In ask_testscripts")

    question = request.json['question']
    language = request.json['language']
    tc_id = request.json['tc_id']
    projectID = request.json['project']

    prompt_fetch_project = f"Fetch project details for project ID '{projectID}' from the database."
    result = agent.chat(prompt_fetch_project)
    
    projectname = result[0]['title']
    testcase = "\n<<<test case>>> \n " + question
    tc_language = "\n<<<language>>> " + language

    # PROMPT
    mainPrompt = "[INST]\n" + myprompts.TS_PERSONA + "\n\n" + myprompts.TS_FORMAT + testcase + tc_language
    prompt_query_engine = f"Query the test script generation engine for project '{projectname}' with the prompt: {mainPrompt}."
    response = agent.chat(prompt_query_engine)

    # database
    tc_record_update = {
        "_id": tc_id,
        "testscript": str(response),
        "projectname": projectname,
        "ts_jira": "",
        "language": language,
        "updatedate": str(datetime.utcnow())
    }
    prompt_save_testscript = f"Create or update a test script record in the database for test case ID '{tc_id}' with data: {tc_record_update}."
    agent.chat(prompt_save_testscript)

    # Prepare response
    answer = {'answer': str(response)}
    logger.debug(answer)
    return jsonify(answer), 200


testscriptoutput_api = Blueprint('testscriptoutputapi', __name__)
@testscriptoutput_api.route('/api/tsoutput/<user>', methods=['POST'])
def testscriptOutput(user):
    logger.debug("In testscriptoutput")

    output = request.json['output']
    testscript_content = request.json['script_content']
    testcase = request.json['testcase']
    projectID = request.json['project']
    tc_jiraid = request.json['tc_jira']

    prompt_fetch_project = f"Fetch project details for project ID '{projectID}' from the database."
    result = agent.chat(prompt_fetch_project)
    
    projectname = result[0]['title']

    # PROMPT
    mainPrompt = myprompts.RCA_PERSONA + " \n <<<TESTCASE>>> \n " + testcase + "\n  <<<TESTSCRIPT>>> \n " + testscript_content + myprompts.RCA_FORMAT + "\n <<<OUTPUT>>> \n" + output
    prompt_query_engine = f"Query the Root Cause Analysis (RCA) engine for project '{projectname}' with the prompt: {mainPrompt}."
    response = agent.chat(prompt_query_engine)

    # Save RCA output to database
    prompt_fetch_rca = f"Fetch RCA document from the database where created by '{user}' and Jira key '{tc_jiraid}'."
    rca = agent.chat(prompt_fetch_rca)
    rca[0]["rcaOutput"] = str(response)
    prompt_save_rca = f"Create or update the RCA record in the database with updated output for created by '{user}' and Jira key '{tc_jiraid}'."
    agent.chat(prompt_save_rca)

    # Prepare response
    answer = {'answer': str(response)}
    logger.debug(answer)
    return jsonify(answer), 200


if __name__ == "__main__":
    app.run(debug=True)
