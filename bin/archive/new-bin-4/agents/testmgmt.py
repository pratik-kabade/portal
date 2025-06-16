import os
import timeit
from datetime import datetime
import json
import random
import subprocess
import time
from bson import json_util
from flask import Blueprint, request, jsonify

from util.genesislogger import GenesisLogger
from llm import LlamaIndexManager
from util import jirautil
from util import testtojson
from db import DBUtil
from rest.project import getProjects
from rest.prompts import myprompts

from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.embeddings import resolve_embed_model

db = os.getenv("MONGODB_NAME")
collection = "testcases"
logger = GenesisLogger.get_instance()

def read_db(projectID):
    result = DBUtil.getDocumentByKeyValue(db,"projects","_id",projectID)
    projectname = result[0]['title']
    DIR = os.path.join("data/",projectname)
    files = len(os.listdir(DIR))
    STD_OUTPUT = [{'tc_id': '0', 'testcase': 'Please upload the document before querying'}]
    if files == 1:
       return STD_OUTPUT
    return str(projectname)

def create_jira_db(userstory_id,projectID,projectname,question,createdBy):
    new_userstory = jirautil.createNewissue(question, question,"Story")
    if userstory_id == "":
        record = {"_id" : str(random.randint(1, 100000)),
        "project" : projectID,
        "projectname" : projectname,
        "jiraid": new_userstory.split('browse/')[1],
        "title" : question,
        "createdby" : createdBy,
        "createddate" :str(datetime.utcnow())
        }
        new_userstory = DBUtil.createOrUpdate(db, "userstories",record)
    return new_userstory

# def create_prompt(question):
#     mainPrompt = "[INST]\n" + myprompts.TC_PERSONA + "\n\n" + myprompts.TC_FORMAT + "\n[/INST]\n" + "<<<USERSTORY>>>\n" + question
#     return mainPrompt

def llm_resp(projectname,question):
    mainPrompt = "[INST]\n" + myprompts.TC_PERSONA + "\n\n" + myprompts.TC_FORMAT + "\n[/INST]\n" + "<<<USERSTORY>>>\n" + question
    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
    queryengine = instance.getQueryEngine(projectname)
    response = queryengine.query(mainPrompt)
    return str(response)

def return_json(response,projectID,userstory_id,new_userstory,createdBy):

    tc_result = testtojson.text_to_json(response)
    tc_json_data = json.loads(str(tc_result))

    resp = []    
    for i, case in enumerate(tc_json_data):
        tc_record = {
        "_id" : str(random.randint(1, 100000)),
        "project" : projectID,
        "userstory" : userstory_id,
        "jirauserstoryId": new_userstory.split('browse/')[1],
        "testcase" : case,
        "tc_title": case.split("Preconditions:")[0],
        "tc_jira" : "",
        "tc_jira_key": "",
        "ts_jira_key" : "",
        "testscript" : "",
        "ts_jira" : "",
        "testScriptStatus" : "Not Executed",
        "bug_id" : "",
        "language" : "",
        "createdby" : createdBy,
        "createddate": str(datetime.utcnow()),
        "updatedate" : ""
        }
        tc_id = DBUtil.createOrUpdate(db, "testcases", tc_record)
        resp.append({"tc_id":tc_id, "testcase" : case})

    return json.loads(json_util.dumps(resp))


def llm_resp_2(projectname,question,language):
    testcase = "\n<<<test case>>> \n " + question
    tc_language = "\n<<<language>>> " + language

    mainPrompt = "[INST]\n" + myprompts.TS_PERSONA + "\n\n" + myprompts.TS_FORMAT + testcase + tc_language
    #mainPrompt = myprompts.TS_PERSONA + testcase + tc_language

    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
    queryengine = instance.getQueryEngine(projectname)
    response = queryengine.query(mainPrompt)
    return str(response)


def return_json_2(tc_id,response,projectname,language):
    ## Save it to DB
    tc_record_update = {
            "_id" : tc_id,
            "testscript" : str(response),
            "projectname": projectname,
            "ts_jira" : "",
            "language" : language,
            "updatedate" : str(datetime.utcnow())
            }
    DBUtil.createOrUpdate(db,"testcases",tc_record_update)

    answer = {'answer' : str(response)}

    logger.debug(answer)
    return jsonify(answer), 200


def llm_resp_3(projectname,testcase,testscript_content,output):
    mainPrompt = myprompts.RCA_PERSONA + " \n <<<TESTCASE>>> \n " + testcase + "\n  <<<TESTSCRIPT>>> \n " + testscript_content + myprompts.RCA_FORMAT + "\n <<<OUTPUT>>> \n" + output 

    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
    queryengine = instance.getQueryEngine(projectname)
    response = queryengine.query(mainPrompt)
    return str(response)


def return_json_3(user,tc_jiraid,response):
    filter = {"createdby": user, "tc_jira_key": tc_jiraid }
    rca = DBUtil.getDocumentByMultipleKeyValue(db, collection, filter)
    rca[0]["rcaOutput"] = str(response)
    DBUtil.createOrUpdate(db, collection, rca[0])
    answer = {'answer' : str(response)}
    logger.debug(answer)
    return jsonify(answer),200










toola = FunctionTool.from_defaults(
    fn=read_db,
    description="""
    Retrieves the project name from the database based on the provided project ID.

    Function:
        read_db(projectID)

    Args:
        projectID (str): The unique identifier for the project.

    Returns:
        str: The name of the project corresponding to the given project ID.
    
    Raises:
        KeyError: If the project ID does not exist in the database.
    """
)

# Define the rest of the tools
toolb = FunctionTool.from_defaults(
    fn=create_jira_db,
    description="""
    Creates a new user story in jira and in the database or updates an existing one.

    Function:
        create_jira_db(userstory_id,projectID,projectname,question,createdBy)

    Args:
        userstory_id (str): The unique identifier for the user story. If empty, a new user story is created.
        projectID (str): The unique identifier for the project.
        projectname (str): The name of the project.
        question (str): The title or description of the user story.
        createdBy (str): The identifier of the user who created the user story.

    Returns:
        str: The unique identifier of the created or updated user story.
    """
)

# toolc = FunctionTool.from_defaults(
#     fn=create_prompt,
#     description="""
#     Constructs a prompt string using a given question.

#     Function:
#         create_prompt(question)

#     Args:
#         question (str): The question to be embedded in the prompt.

#     Returns:
#         str: The newly constructed prompt.
#     """
# )

toold = FunctionTool.from_defaults(
    fn=llm_resp,
    description="""
    Generates a response from a language model based on the given project name and question.

    Function:
        llm_resp(projectname, question)

    Args:
        projectname (str): The name of the project for which the query engine is to be used.
        question (str): The question to be embedded in the prompt and sent to the language model.

    Returns:
        response (str): The response from the language model.

    Raises:
        KeyError: If the project name does not exist in the query engine.
    """
)

toole = FunctionTool.from_defaults(
    fn=return_json,
    description="""
    Generates and returns JSON records of test cases from a given response, associating them with a specific project and user story.

    Function:
        return_json(response, projectID, userstory_id, new_userstory, createdBy)

    Args:
        response (str): The response text containing test case information.
        projectID (str): The ID of the project associated with the test cases.
        userstory_id (str): The ID of the user story associated with the test cases.
        new_userstory (str): The new Jira user story URL containing the user story details.
        createdBy (str): The user responsible for creating the test cases.

    Returns:
        List[dict]: A list of dictionaries containing the newly created test case IDs and test case content.

    Raises:
        ValueError: If an error occurs during the conversion of test cases to JSON format.
    """
)

toold_2 = FunctionTool.from_defaults(
    fn=llm_resp_2,
    description="""
    Generates a response from a language model based on the given project name and question.

    Function:
        llm_resp(projectname, question, language)

    Args:
        projectname (str): The name of the project for which the query engine is to be used.
        question (str): The question to be embedded in the prompt and sent to the language model.
        language (str): The language to be used in getting prompt

    Returns:
        response (str): The response from the language model.

    Raises:
        KeyError: If the project name does not exist in the query engine.
    """
)

toole_2 = FunctionTool.from_defaults(
    fn=return_json_2,
    description="""
    Generates and returns JSON records of test cases from a given response, associating them with a specific project and user story.

    Function:
        return_json_2(tc_id,response,projectname,language):

    Args:
        tc_id (str): The text containing test case id.
        response (str): The response text containing test script information.
        projectname (str): The name of the project for which the query engine is to be used.
        language (str): The language to be used in getting prompt

    Returns:
        List[dict]: A list of dictionaries containing the newly created test case IDs and test case content.

    Raises:
        ValueError: If an error occurs during the conversion of test cases to JSON format.
    """
)

toold_3 = FunctionTool.from_defaults(
    fn=llm_resp_3,
    description="""
    Generates a response from a language model based on the given project name and question.

    Function:
        llm_resp_3(projectname,testcase,testscript_content,output):

    Args:
        projectname (str): The name of the project for which the query engine is to be used.
        testcase (str): The testcase from user
        testscript_content (str): The testscript_content from user
        output (str): The output from user

    Returns:
        response (str): The response from the language model.

    Raises:
        KeyError: If the project name does not exist in the query engine.
    """
)


toole_3 = FunctionTool.from_defaults(
    fn=return_json_3,
    description="""
    Generates and returns JSON records of test cases from a given response, associating them with a specific project and user story.

    Function:
        return_json_3(user,tc_jiraid,response):

    Args:
        user (str): The text containing test case id.
        tc_jiraid (str): The text containing jira test case id.
        response (str): The response text containing test script information.

    Returns:
        List[dict]: A list of dictionaries containing the newly created response.

    Raises:
        ValueError: If an error occurs during the conversion of test cases to JSON format.
    """
)











# Configure the LLM model
Settings.llm = Ollama(model="llama3", request_timeout=60.0, temperature=0)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

# Create an agent using the defined tools
tc_agent = ReActAgent.from_tools(
    tools=[toola, toolb, toold, toole],
    llm=Settings.llm,
    verbose=True
)

# Create an agent using the defined tools
ts_agent = ReActAgent.from_tools(
    tools=[toola, toold_2, toole_2],
    llm=Settings.llm,
    verbose=True
)

# Create an agent using the defined tools
op_agent = ReActAgent.from_tools(
    tools=[toola, toold_3, toole_3],
    llm=Settings.llm,
    verbose=True
)















asktestcases_api = Blueprint('asktestcases_api', __name__)
@asktestcases_api.route('/api/ask/tm/testcases', methods=['POST'])
def ask_testcases():
    logger.debug("In ask_testcases")

    # Extract the incoming JSON request data
    question = request.json['question']
    createdBy = request.json['user']
    projectID = request.json['project']
    userstory_id = request.json['userstory_id']

    # Combine all tasks into a single prompt
    combined_prompt = f"""
Step 1: Retrieve the project name using the project ID.
projectname = read_db({projectID})

Step 2: Create or update the user story in the database using the details and also use project name retrieved earlier.
new_userstory = create_jira_db({userstory_id}, {projectID}, projectname, {question}, {createdBy})

Step 3: Generate the response from the language model by using the question.
tc_result = llm_resp(projectname, question)

Step 4: Convert the response to JSON and store it in the database and return whatever the JSON we got from the function as it is
response_json = return_json(tc_result, {projectID}, {userstory_id}, new_userstory, {createdBy})
    """
    

    response_gen = tc_agent.chat(combined_prompt)

    return str(response_gen)




# BIN
asktestscripts_api = Blueprint('asktestscripts_api', __name__)
@asktestscripts_api.route('/api/ask/tm/testscripts', methods=['POST'])
def ask_testscripts():
    logger.debug("in ask_testscripts")

    question = request.json['question']
    language = request.json['language']
    tc_id = request.json['tc_id']
    projectID = request.json['project']


    # Combine all tasks into a single prompt
    combined_prompt = f"""
Step 1: Retrieve the project name using the project ID.
projectname = read_db({projectID})

Step 2: Create or update the user story in the database using the details and also use project name retrieved earlier.
new_userstory = create_jira_db({userstory_id}, {projectID}, projectname, {question}, {createdBy})

Step 3: Generate the response from the language model by using the question.
tc_result = llm_resp(projectname, question)

Step 4: Convert the response to JSON and store it in the database and return whatever the JSON we got from the function as it is
response_json = return_json(tc_result, {projectID}, {userstory_id}, new_userstory, {createdBy})
    """
    
    response_gen = agent.chat(combined_prompt)

    return str(response_gen)


testscriptoutput_api = Blueprint('testscriptoutputapi', __name__)
@testscriptoutput_api.route('/api/tsoutput/<user>', methods=['POST'])
def testscriptOutput(user):
    logger.debug("in testscriptoutput")

    output = request.json['output']
    testscript_content = request.json['script_content']
    testcase = request.json['testcase']
    projectID = request.json['project']
    tc_jiraid = request.json['tc_jira']


    # Combine all tasks into a single prompt
    combined_prompt = f"""
Step 1: Retrieve the project name using the project ID.
projectname = read_db({projectID})

Step 2: Create or update the user story in the database using the details and also use project name retrieved earlier.
new_userstory = create_jira_db({userstory_id}, {projectID}, projectname, {question}, {createdBy})

Step 3: Generate the response from the language model by using the question.
tc_result = llm_resp(projectname, question)

Step 4: Convert the response to JSON and store it in the database and return whatever the JSON we got from the function as it is
response_json = return_json(tc_result, {projectID}, {userstory_id}, new_userstory, {createdBy})
    """
    
    response_gen = agent.chat(combined_prompt)

    return str(response_gen)


    ## Save it to DB
    filter = {"createdby": user, "tc_jira_key": tc_jiraid }
    rca = DBUtil.getDocumentByMultipleKeyValue(db, collection, filter)
    rca[0]["rcaOutput"] = str(response)
    DBUtil.createOrUpdate(db, collection, rca[0])
    answer = {'answer' : str(response)}
    logger.debug(answer)
    return jsonify(answer),200

# curl -X POST -H "Content-Type: application/json" -d '{"question" : "As a system admin, I shall be able to fetch value of parameter Device.X_CISCO_COM_DeviceControl.SSHEnable using dmcli command", "user" : "admin", "project" : "10391", "userstory_id" : "4333716"}' http://localhost:3000/api/ask/tm/testcases
