import os
import timeit
from datetime import datetime
import json
import random
from bson import json_util
from rest.prompts import myprompts
from flask import Blueprint, request, jsonify

import subprocess
from rest import executionEngine
from llm import LlamaIndexManager
from util.genesislogger import GenesisLogger
from util import util
from util import testtojson
from db import DBUtil
import time
from rest.project import getProjects
from util import jirautil

db = os.getenv("MONGODB_NAME")
collection = "testcases"

# Instantiating Logger
logger = GenesisLogger.get_instance()

issue_type = "Bug"
linktype = "is blocked by"

executescript_api = Blueprint('executescriptapi', __name__)
@executescript_api.route('/api/execute/<user>', methods=['POST'])
def executeScript(user):
    projectID = request.json['project']
    result = DBUtil.getDocumentByKeyValue(db,"projects","_id",projectID)
    projectname = result[0]['title'].lower()
    script_content = request.json["script_content"]
    script_content = executionEngine.engine(script_content)
    print(script_content)
    tc_jira = request.json['tc_jira']
    tc_issue = request.json['tc_issue']
    ts_jira_key = request.json['ts_jira_key']
    if "rdk" in projectname:
        script_result = executeScriptRDK(script_content, tc_jira, tc_issue, user, ts_jira_key)
    elif projectname == "cisco":
        script_result = executeScriptCisco(script_content, tc_jira, tc_issue,user, ts_jira_key)
    else:
        script_result = { "status": "error", "message": "Unsupported project name" }
    return script_result

def executeScriptRDK(script_content,tc_jira, tc_issue, user, ts_jira_key):
    SCRIPT_FOLDER = str(os.getenv("SCRIPT_FOLDER"))
    if not script_content:
        return jsonify({"status": "fail","error": "Missing script content in request body"}), 400

    try:
       script_name = generate_randomscript_name()
       script_path = os.path.join(SCRIPT_FOLDER, script_name)

       os.makedirs(SCRIPT_FOLDER, exist_ok=True)
       with open(script_path, "w") as f:
           f.write(script_content)
    except Exception as e:
       return jsonify({"status": "fail","error": f"Error creating temporary script: {str(e)}"}), 500

    try:
       with open(script_path, "r") as f:
         script_lines = f.readlines()
       for line in script_lines:
         if line.startswith("import"):
           package_name = line.split()[1].strip()
           try:
             __import__(package_name)
           except ImportError:
             return jsonify({"status": "fail","error": f"Missing package: {package_name}.Please install it before running the  script."}), 501
    except Exception as e:
       pass

    try:
        process = subprocess.Popen(["python3", script_path],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        output, _  = process.communicate()
        exit_code = process.returncode

        current_status_ts = jirautil.get_issue_status(ts_jira_key)
        current_status_tc = jirautil.get_issue_status(tc_jira)
        print(current_status_tc, current_status_ts)

        if (current_status_tc == "Not Executed"  and current_status_ts == "Not Executed"):
           jirautil.status_transition(tc_jira,'6')
           jirautil.status_transition(ts_jira_key, '6')
        elif (current_status_tc == "Done"  and current_status_ts == "Done"):
           jirautil.status_transition(tc_jira,'7')
           jirautil.status_transition(ts_jira_key, '7')
        elif (current_status_tc == "FAILED"  and current_status_ts == "FAILED"):
           jirautil.status_transition(tc_jira,'4')
           jirautil.status_transition(ts_jira_key, '4')

        summary = ""
        description = ""
        keywords = {"error","exception","traceback","can't find","not found"}
        if exit_code == 0:
            for word in keywords:
                if word in output.lower():

                    # Update the status of jira ticket to Fail
                    jirautil.status_transition(ts_jira_key,'3')
                    jirautil.status_transition(tc_jira,'3')

                    # Create Jira ticket
                    summary = tc_jira
                    description = output
                    bug = jirautil.createNewIssueAndLink(summary, description, issue_type,tc_jira, linktype)

                    # Save in DB
                    filter = {"createdby" : "admin", "tc_jira": tc_issue}
                    testcase = DBUtil.getDocumentByMultipleKeyValue(db,collection, filter)
                    testcase[0]["testScriptOutput"] = output
                    testcase[0]["testScriptStatus"] = 'Failed'
                    testcase[0]["bug_id"] = bug
                    DBUtil.createOrUpdate(db, collection, testcase[0])
                    return_dict = {"status": "failed", "output": output, "bug_id": bug}
                    break
            else:
                return_dict = {"status": "passed", "output": output}

                # Update the status of jira ticket to Pass
                jirautil.status_transition(tc_jira,'2')
                jirautil.status_transition(ts_jira_key,'2')
                jirautil.status_transition(tc_jira,'5')
                jirautil.status_transition(ts_jira_key,'5')

                # Save in DB
                filter = {"createdby" : "admin", "tc_jira": tc_issue}
                testcase = DBUtil.getDocumentByMultipleKeyValue(db,collection, filter)
                testcase[0]["testScriptOutput"] = output
                testcase[0]["testScriptStatus"] = 'Passed'
                DBUtil.createOrUpdate(db, collection, testcase[0])
        else:
            # Update the status of jira ticket to Fail
            jirautil.status_transition(ts_jira_key,'3')
            jirautil.status_transition(tc_jira,'3')

            # Create jira ticket for bug
            summary = tc_jira
            description = output
            bug = jirautil.createNewIssueAndLink(summary, description,issue_type, tc_jira, linktype)

            # Save in DB
            filter = {"createdby": user, "tc_jira": tc_issue}
            testcase = DBUtil.getDocumentByMultipleKeyValue(db, collection, filter)
            testcase[0]["testScriptOutput"] = output
            testcase[0]["testScriptStatus"] = "Failed"
            testcase[0]["bug_id"] = bug
            DBUtil.createOrUpdate(db, "testcases", testcase[0])
            return_dict = {"status": "failed", "output": output, "bug_id" : bug}

        return return_dict
    except FileNotFoundError as ex:
       print(ex)
       return jsonify({"status": "fail","output": "Error executing script"}), 502
    except Exception as e:
       print(e)
       logger.error(str(e))
       return jsonify({"status": "fail","output": "Internal server error"}), 503

def executeScriptCisco(script_content,tc_jira,tc_issue,user, ts_jira_key):
    SCRIPT_FOLDER = str(os.getenv("SCRIPT_FOLDER"))
    if not script_content:
        return jsonify({"status": "fail","error":"Missing script content in request body"}), 400
    try:
        script_name = generate_randomscript_name()
        script_path = os.path.join(SCRIPT_FOLDER, script_name)
        os.makedirs(SCRIPT_FOLDER, exist_ok=True)
        with open(script_path, "w") as f:
            f.write(script_content)
    except Exception as e:
        return jsonify({"status": "fail","error": f"Error creating temporary script: {str(e)}"}), 500
    try:
        with open(script_path, "r") as f:
            script_lines = f.readlines()
            for line in script_lines:
                if line.startswith("import"):
                    package_name = line.split()[1].strip()
                    try:
                         __import__(package_name)
                    except ImportError:
                        return jsonify({"status": "fail","error": f"Missing package: {package_name}.Please install it before running the script."}), 501
    except Exception as e:
        pass

    try:
        process = subprocess.Popen(["python3", script_path],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        output, _ = process.communicate()
        exit_code = process.returncode

        # Update the jira ticket to InProgress
        jirautil.status_transition(ts_jira_key,'6')
        jirautil.status_transition(tc_jira,'6')

        print("exit_code",exit_code)
        keywords = {"error","exception","traceback","can't find","not found"}
        if exit_code == 0:
            #if "error" in output.lower() or "exception" in output.lower() or "traceback" in output.lower() or "can't find" in output.lower():
            for word in keywords:
                if word in output.lower():
                    # Update the status of jira ticket
                    jirautil.status_transition(ts_jira_key,'3')
                    jirautil.status_transition(tc_jira,'3')

                    # Create Jira ticket for bug
                    summary = tc_jira
                    description = output
                    bug = jirautil.createNewIssueAndLink(summary, description, issue_type, tc_jira, linktype)

                    # Save in DB
                    filter = {"createdby" : "admin", "tc_jira": tc_issue}
                    testcase = DBUtil.getDocumentByMultipleKeyValue(db,collection, filter)
                    testcase[0]["testScriptOutput"] = output
                    testcase[0]["testScriptStatus"] = 'FAIL'
                    testcase[0]["bug_id"] = bug
                    DBUtil.createOrUpdate(db, collection, testcase[0])
                    return_dict = {"status": "fail", "output": output, "bug_id" : bug}
                    break
                else:
                    return_dict = {"status": "pass", "output": output}

                    # Save in DB
                    filter = {"createdby" : "admin", "tc_jira": tc_issue}
                    testcase = DBUtil.getDocumentByMultipleKeyValue(db,collection, filter)
                    testcase[0]["testScriptOutput"] = output
                    testcase[0]["testScriptStatus"] = 'PASS'
                    DBUtil.createOrUpdate(db, collection, testcase[0])

                    # Update the status of jira ticket to Pass
                    jirautil.status_transition(ts_jira_key,'2')
                    jirautil.status_transition(tc_jira,'2')
        else:

            # Update the status of jira ticket to Fail
            jirautil.status_transition(ts_jira_key,'3')
            jirautil.status_transition(tc_jira,'3')

            # Create Jira ticket for bug
            summary = tc_jira
            description = output
            bug =jirautil.createNewIssueAndLink(summary, description, issue_type, tc_jira, linktype)

            # Save in DB
            filter = {"createdby" : "admin", "tc_jira": tc_issue}
            testcase = DBUtil.getDocumentByMultipleKeyValue(db,collection, filter)
            testcase[0]["testScriptOutput"] = output
            testcase[0]["testScriptStatus"] = 'FAIL'
            testcase[0]["bug_id"] = bug
            DBUtil.createOrUpdate(db, collection, testcase[0])
            return_dict = {"status": "fail", "output": output, "bug_id" : bug}
        return return_dict
    except FileNotFoundError:
        return jsonify({"status": "fail","output": "Error executing script"}), 502
    except Exception as e:
        logger.error(str(e))
        return jsonify({"status": "fail","output": "Internal server error"}), 503

def generate_randomscript_name():
    return f"{os.urandom(8).hex()}.py"


