import os
import timeit
from datetime import datetime
import json
import random
from bson import json_util
from rest.prompts import myprompts
from flask import Blueprint, request, jsonify

import subprocess
from llm import LlamaIndexManager
from util.genesislogger import GenesisLogger
from util import util
from util import jirautil
from util import testtojson
from db import DBUtil
import time
from rest.project import getProjects

db = os.getenv("MONGODB_NAME")
collection = "testcases"

# Instantiating Logger
logger = GenesisLogger.get_instance()

# Define a blueprint for your asktype route
asktestcases_api = Blueprint('asktestcases_api', __name__)
@asktestcases_api.route('/api/ask/tm/testcases', methods=['POST'])
def ask_testcases():
   logger.debug("In ask_testcases")

   question = request.json['question']
   #semantic_search = request.json.get('semantic_search', False)
   createdBy = request.json['user']
   projectID = request.json['project']
   userstory_id = request.json['userstory_id']

   result = DBUtil.getDocumentByKeyValue(db,"projects","_id",projectID)

   projectname = result[0]['title']
   DIR = os.path.join("data/",projectname)
   files = len(os.listdir(DIR))
   STD_OUTPUT = [{'tc_id': '0', 'testcase': 'Please upload the document before querying'}]
   if files == 1:
      return STD_OUTPUT

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

   mainPrompt = "[INST]\n" + myprompts.TC_PERSONA + "\n\n" + myprompts.TC_FORMAT + "\n[/INST]\n" + "<<<USERSTORY>>>\n" + question

   instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
   queryengine = instance.getQueryEngine(projectname)
   response = queryengine.query(mainPrompt)

   tc_result = testtojson.text_to_json(str(response))

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

# Define a blueprint for your asktype route
asktestscripts_api = Blueprint('asktestscripts_api', __name__)
@asktestscripts_api.route('/api/ask/tm/testscripts', methods=['POST'])
def ask_testscripts():
   logger.debug("in ask_testscripts")

   question = request.json['question']
   language = request.json['language']
   tc_id = request.json['tc_id']
   projectID = request.json['project']
   result = DBUtil.getDocumentByKeyValue(db,"projects","_id",projectID)
   projectname = result[0]['title']
   testcase = "\n<<<test case>>> \n " + question
   tc_language = "\n<<<language>>> " + language

   mainPrompt = "[INST]\n" + myprompts.TS_PERSONA + "\n\n" + myprompts.TS_FORMAT + testcase + tc_language
   #mainPrompt = myprompts.TS_PERSONA + testcase + tc_language

   instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
   queryengine = instance.getQueryEngine(projectname)
   response = queryengine.query(mainPrompt)

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

testscriptoutput_api = Blueprint('testscriptoutputapi', __name__)
@testscriptoutput_api.route('/api/tsoutput/<user>', methods=['POST'])
def testscriptOutput(user):
    logger.debug("in testscriptoutput")

    output = request.json['output']
    testscript_content = request.json['script_content']
    testcase = request.json['testcase']
    projectID = request.json['project']
    result = DBUtil.getDocumentByKeyValue(db,"projects","_id",projectID)
    projectname = result[0]['title']
    tc_jiraid = request.json['tc_jira']
    mainPrompt = myprompts.RCA_PERSONA + " \n <<<TESTCASE>>> \n " + testcase + "\n  <<<TESTSCRIPT>>> \n " + testscript_content + myprompts.RCA_FORMAT + "\n <<<OUTPUT>>> \n" + output 

    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
    queryengine = instance.getQueryEngine(projectname)
    response = queryengine.query(mainPrompt)

    ## Save it to DB
    filter = {"createdby": user, "tc_jira_key": tc_jiraid }
    rca = DBUtil.getDocumentByMultipleKeyValue(db, collection, filter)
    rca[0]["rcaOutput"] = str(response)
    DBUtil.createOrUpdate(db, collection, rca[0])
    answer = {'answer' : str(response)}
    logger.debug(answer)
    return jsonify(answer),200

