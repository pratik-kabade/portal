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

def a(projectID):
   result = DBUtil.getDocumentByKeyValue(db,"projects","_id",projectID)
   projectname = result[0]['title']
   # DIR = os.path.join("data/",projectname)
   # files = len(os.listdir(DIR))
   # STD_OUTPUT = [{'tc_id': '0', 'testcase': 'Please upload the document before querying'}]
   # if files == 1:
   #    return STD_OUTPUT
   return projectname

def b(userstory_id,projectID,projectname,question,createdBy):
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
       userstory_id = DBUtil.createOrUpdate(db, "userstories",record)
       return userstory_id

def c():
   mainPrompt = "[INST]\n" + myprompts.TC_PERSONA + "\n\n" + myprompts.TC_FORMAT + "\n[/INST]\n" + "<<<USERSTORY>>>\n" + question
   return mainPrompt

def d(projectname,mainPrompt):
   instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
   queryengine = instance.getQueryEngine(projectname)
   response = queryengine.query(mainPrompt)
   tc_result = testtojson.text_to_json(str(response))
   return tc_result

def e(tc_result,projectID,userstory_id,createdBy):
   resp = []
   tc_json_data = json.loads(tc_result)
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


toola = FunctionTool.from_defaults(
    fn=a,
    description='Retrieves the project name using projectID'
)

# Define the rest of the tools
toolb = FunctionTool.from_defaults(
    fn=b,
    description='Creates or updates the user story in the project.'
)

toolc = FunctionTool.from_defaults(
    fn=c,
    description='Generates the main prompt for querying test cases.'
)

toold = FunctionTool.from_defaults(
    fn=d,
    description='Queries the project for test cases based on the provided prompt.'
)

toole = FunctionTool.from_defaults(
    fn=e,
    description='Processes and saves the test case results and returns them in a JSON format.'
)

# Configure the LLM model
Settings.llm = Ollama(model="llama3", request_timeout=60.0, temperature=0)
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

# Create an agent using the defined tools
agent = ReActAgent.from_tools(
    tools=[toola, toolb, toolc, toold, toole],
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
   Step 1: Retrieve the project name using projectID: {projectID}.
      - Store this result as 'projectname'.
      - Return the 'projectname'.
   Step 2: Create or update the user story for the project:
      - Use the following details:
       * projectID: {projectID}
       * projectname: (use the 'projectname' from Step 1)
       * question: {question}
       * createdBy: {createdBy}
      - Return the 'userstory_id' after creating or updating the user story.
   Step 3: Generate the main prompt for querying test cases:
      - Use the following:
       * userstory_id: (from Step 2)
       * question: {question}
      - Return the generated 'mainPrompt'.
   Step 4: Query the test cases:
      - Use the following:
       * projectname: (from Step 1)
       * mainPrompt: (from Step 3)
      - Return the 'tc_result' after querying the test cases.
   Step 5: Process and save the test case results:
      - Use the following:
       * projectID: {projectID}
       * userstory_id: (from Step 2)
       * createdBy: {createdBy}
       * tc_result: (from Step 4)
      - Return the saved test cases in a JSON format.
   """

   '''
   combined_prompt = f"""
   1. Retrieve the project name using projectID: {projectID}. Store this result as `projectname` and return it
   2. Create or update the user story for projectID: {projectID}, with projectname based on the previous step, question: {question}, and createdBy: {createdBy}
   3. Generate the main prompt for querying test cases based on the user story for question: {question}
   4. Query test cases for the project and main prompt generated
   5. Process and save the test case results, with projectID: {projectID}, userstory_id: {userstory_id}, and createdBy: {createdBy}
   """
   '''
   # Use agent.chat only once to perform all tasks
   response = agent.chat(combined_prompt)

   return jsonify(response)



'''
asktestcases_api = Blueprint('asktestcases_api', __name__)
@asktestcases_api.route('/api/ask/tm/testcases', methods=['POST'])
def ask_testcases():
   logger.debug("In ask_testcases")

   question = request.json['question']
   createdBy = request.json['user']
   projectID = request.json['project']
   userstory_id = request.json['userstory_id']

   # result = DBUtil.getDocumentByKeyValue(db,"projects","_id",projectID)

   # projectname = result[0]['title']
   # DIR = os.path.join("data/",projectname)
   # files = len(os.listdir(DIR))
   # STD_OUTPUT = [{'tc_id': '0', 'testcase': 'Please upload the document before querying'}]
   # if files == 1:
   #    return STD_OUTPUT

   # new_userstory = jirautil.createNewissue(question, question,"Story")
   # if userstory_id == "":
   #     record = {"_id" : str(random.randint(1, 100000)),
   #                  "project" : projectID,
   #                  "projectname" : projectname,
   #                  "jiraid": new_userstory.split('browse/')[1],
   #                  "title" : question,
   #                  "createdby" : createdBy,
   #                  "createddate" :str(datetime.utcnow())
   #              }
   #     userstory_id = DBUtil.createOrUpdate(db, "userstories",record)

   # mainPrompt = "[INST]\n" + myprompts.TC_PERSONA + "\n\n" + myprompts.TC_FORMAT + "\n[/INST]\n" + "<<<USERSTORY>>>\n" + question

   # instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
   # queryengine = instance.getQueryEngine(projectname)
   # response = queryengine.query(mainPrompt)

   # tc_result = testtojson.text_to_json(str(response))

   # resp = []
   # tc_json_data = json.loads(tc_result)
   # for i, case in enumerate(tc_json_data):
   #      tc_record = {
   #            "_id" : str(random.randint(1, 100000)),
   #            "project" : projectID,
   #            "userstory" : userstory_id,
   #            "jirauserstoryId": new_userstory.split('browse/')[1],
   #            "testcase" : case,
   #            "tc_title": case.split("Preconditions:")[0],
   #            "tc_jira" : "",
   #            "tc_jira_key": "",
   #            "ts_jira_key" : "",
   #            "testscript" : "",
   #            "ts_jira" : "",
   #            "testScriptStatus" : "Not Executed",
   #            "bug_id" : "",
   #            "language" : "",
   #            "createdby" : createdBy,
   #            "createddate": str(datetime.utcnow()),
   #            "updatedate" : ""
   #            }
   #      tc_id = DBUtil.createOrUpdate(db, "testcases", tc_record)
   #      resp.append({"tc_id":tc_id, "testcase" : case})

   # return json.loads(json_util.dumps(resp))
'''










# BIN
asktestscripts_api = Blueprint('asktestscripts_api', __name__)
@asktestscripts_api.route('/api/ask/tm/testscripts', methods=['POST'])
def ask_testscripts():
   pass

testscriptoutput_api = Blueprint('testscriptoutputapi', __name__)
@testscriptoutput_api.route('/api/tsoutput/<user>', methods=['POST'])
def testscriptOutput(user):
   pass
