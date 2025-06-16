from flask import Blueprint, request, jsonify, send_file
from bson import json_util
import os
import timeit
from db import DBUtil
from util.genesislogger import GenesisLogger
from util import jirautil
import json
from datetime import datetime

from flask_cors import CORS 


# Instantiating Logger
logger = GenesisLogger.get_instance()

db = os.getenv("MONGODB_NAME")
collection = "settings"

PORT = os.getenv('PORT')

getjirasettings_api = Blueprint('getjirasettings_api', __name__)
@getjirasettings_api.route('/api/settings/jira', methods=['GET'])
def getsettings_jira():
    logger.debug("GET API: Settings/jira")

    """Retrieve files metadata from MongoDB and return as JSON."""
    try:
        result = DBUtil.getDocumentByKeyValue(db,collection,"SETTINGS_TYPE","JIRA")
        logger.debug(result)


        return json.loads(json_util.dumps(result))
    except Exception as e:
        logger.error(e)
        # If an error occurs during the retrieval process, return a JSON response with an error message and status code 500 (Internal Server Error
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

createjirasettings_api = Blueprint('createjirasettings_api', __name__)
@createjirasettings_api.route('/api/settings/jira', methods=['PUT'])
def createsettings_jira():
    logger.debug("POST API :  Settings/jira")

    try:
        data = request.get_json()
        result = DBUtil.createOrUpdate(db,collection,data)
        # Return success message along with file ID as JSON response
        return jsonify({'message': 'File uploaded and stored successfully!'}), 200
    except Exception as e:
        logger.error(e)
        # If an error occurs while storing the file, delete the file and return an error message
        return jsonify({'error': f'Error adding document : {str(e)}'}), 500

deletejirasettings_api = Blueprint('deletejirasettings_api', __name__)
@deletejirasettings_api.route('/api/settings/jira/<_id>', methods=['DELETE'])
def delsettings_jira(_id):
    logger.debug("DELETE API : Settings/jira")

    try:
        delcount = DBUtil.delete_document_by_id(db,collection,_id)
        if delcount == 1:
            return jsonify({"message":"delete successfull"}),200
        else:
            return jsonify({'error': 'Error deleting document,  no record found'}), 500
    except Exception as ex:
        logger.error(ex)
        # If an error occurs while storing the file, delete the file and return an error message
        return jsonify({'error': f'Error deleting document : {str(ex)}'}), 500

createjira_api = Blueprint('createjira_api', __name__)
@createjira_api.route('/api/jira/<user>', methods=['POST'])
def create_jira(user):
    logger.debug("CREATE JIRA")
    try:
        summary = request.json['summary']
        description = f"Test Case and test steps for {summary}"
        issue_type = "TestCase"
        linktype = "Tested by"
        tc_id = "1000"
        if request.json['tc_id']:
           tc_id = request.json['tc_id']

        filter = { "createdby": user, "_id": tc_id }
        res = DBUtil.getDocumentByMultipleKeyValue(db, "testcases", filter)
        parentkey = res[0]['jirauserstoryId']

        issue = jirautil.createNewIssueAndLink(summary, description, issue_type, parentkey, linktype)
        response = {'issue':issue}

        ## Now update testcase in DB
        tc_record_update = {
                "_id" : str(tc_id),
                "tc_jira" : issue,
                "tc_jira_key": issue.split('browse/')[1],
                "updatedate" : str(datetime.utcnow())
                }

        DBUtil.createOrUpdate(db, "testcases",tc_record_update)

        return jsonify(response),201
    except Exception as e:
        logger.debug(e)
        return jsonify({'error':f'Error creating jira issue : {str(e)}'}), 500

updatejira_api = Blueprint('updatejira_api', __name__)
@updatejira_api.route('/api/jira/<jiraid>', methods=['PUT'])
def update_jira(jiraid):
    logger.debug("UPDATE JIRA: JIRA SETTINGS")
    try:
        tc_id = request.json['tc_id']
        testcase = request.json['testcase']

        #print(f"CREATE JIRA  TEST CASES: ", testcase)

        ## Now update testcase in DB
        tc_record_update = {
                "_id" : str(tc_id),
                "testcase" : testcase,
                "updatedate" : datetime.utcnow()
                }

        DBUtil.createOrUpdate(db, "testcases",tc_record_update)
        issue = jirautil.updateJira(jiraid, testcase)
        response = {'response':'success'}
        return jsonify(response),200
    except Exception as e:
        logger.error(e)
        return jsonify({'error':f'Error creating jira issue : {str(e)}'}), 500

create_child_jira_api = Blueprint('create_child_jira_api', __name__)
@create_child_jira_api.route('/api/jira/createchild', methods=['POST'])
def create_child_jira():
    logger.debug("CREATE CHILD JIRA in JIRA SETTINGS")
    try:

        parentKey = request.json['parentkey']
        summary = request.json['testcase_title']
        description = request.json['testscript']
        issue_type = "TestScript"
        linktype = "Tested by"

        tc_id = "1000"
        if request.json['tc_id']:
           tc_id = request.json['tc_id']


        issue = jirautil.createNewIssueAndLink(summary, description, issue_type, parentKey, linktype)
        tc_record_update = {
                "_id" : tc_id,
                "ts_jira" : issue,
                "ts_jira_key" : issue.split('browse/')[1],
                "updatedate" : datetime.utcnow()
                }
        DBUtil.createOrUpdate(db,"testcases",tc_record_update)
        response = {'issue':str(issue)}
        return jsonify(response),200
    except Exception as e:
        logger.error(e)
        return jsonify({'error':f'Error creating jira issue : {str(e)}'}), 500

updatechildjira_api = Blueprint('updatechildjira_api', __name__)
@updatechildjira_api.route('/api/jira/updatechild', methods=['PUT'])
def updatechild_jira():
    logger.debug("UPDATE CHILD JIRA IN JIRA SETTINGS")
    try:
        ts_jira = request.json['jira_id']
        tc_id = request.json['tc_id']
        testscript = request.json['testscript']

        #print(f"CREATE JIRA  TEST SCRIPTS:  ", testscript)

        ## Now update testscript in DB
        ts_record_update = {
                "_id" : str(tc_id),
                "testscript" : testscript,
                "updatedate" : datetime.utcnow()
                }


        DBUtil.createOrUpdate(db, "testcases",ts_record_update)
        issue = jirautil.updateJira(ts_jira, testscript)
        response = {'response':'success'}
        return jsonify(response),200
    except Exception as e:
        logger.error(e)
        return jsonify({'error':f'Error creating jira issue : {str(e)}'}), 500



getjiraproject_api = Blueprint('getjiraproject_api', __name__)
@getjiraproject_api.route('/api/jira/projects/', methods=['GET'])
def projects():
    try:
        projects = jirautil.get_projects()
        return jsonify(projects)
    except Exception as error:
        return jsonify({'error': 'An error occurred fetching the projects.'}), 500

getjirauserstories_api = Blueprint('getjirauserstories_api', __name__)
@getjirauserstories_api.route('/api/jira/userstory/<projectkey>', methods=['GET'])
def userstories(projectkey):
    try:
        issues = jirautil.get_userstories(projectkey)
        return jsonify(issues)
    except Exception as error:
        return jsonify({'error': 'An error occurred fetching the issues.'}), 500
