from flask import Blueprint, request, jsonify
from db import DBUtil
from util.genesislogger import GenesisLogger
from datetime import datetime
import os
import random
import json
from bson import json_util

# Instantiating Logger
logger = GenesisLogger.get_instance()

db = os.getenv("MONGODB_NAME")
collection = "testcases"

gettestcases_api = Blueprint('gettestcases_api', __name__)
@gettestcases_api.route('/api/testcases/<user>/<_id>', methods=['GET'])
def getTestCases(user,_id):
    logger.debug("GET /testcases")

    try:
        filter = {"createdby" : user,"userstory":_id}
        result = DBUtil.getDocumentByMultipleKeyValue(db,collection,filter)
        logger.debug(result)

        #return jsonify({"answer" : result}),200
        return jsonify({"response":json.loads(json_util.dumps(result))}),200
    except Exception as e:
        logger.error(e)
        # If an error occurs during the retrieval process, return a JSON response with an error message and status code 500 (Internal Server Error
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

getmultipletestcases_api = Blueprint('getmultipletestcases_api', __name__)
@getmultipletestcases_api.route('/api/testcases/<user>', methods=['POST'])
def getmultipletestcases(user):
    logger.debug("POST /testcases")

    try:
        userstories = request.json['userstories']
        response = []
        for us in userstories:
            filter = {"createdby" : user,"userstory":us['_id']}
            result = DBUtil.getDocumentByMultipleKeyValue(db,collection,filter)

            for res in result:
                record = {
                             "project": res['project'],
                             "userstory": res['jirauserstoryId'],
                             "testcases": res['testcase'],
                             "tc_jira_key": res['tc_jira_key'],
                             "testscripts": res['testscript'],
                             "ts_jira_key": res['ts_jira_key']
                          }

                response.append(record);

        return jsonify({"response":json.loads(json_util.dumps(response))}),200

    except Exception as e:
        logger.error(e)
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500


getProjectData_api = Blueprint('getProjectData_api', __name__)
@getProjectData_api.route('/api/projectData/<user>', methods=['POST'])
def getProjectData(user):
    logger.debug("POST /projectData")

    try:
        projects = request.json['projects']
        response = []
        for project in projects:
            filter1 = {"createdby": user, "project": project['_id']}
            userstories = DBUtil.getDocumentByMultipleKeyValue(db, "userstories", filter1)

            for us in userstories:
               filter2 = {"createdby": user, "userstory": us['_id']}
               result = DBUtil.getDocumentByMultipleKeyValue(db, "testcases", filter2)

               for res in result:
                   record = {
                               "project": project['title'],
                               "userstory": us['jiraid'],
                               "testcase": res['testcase'],
                               "tc_jira_key": res['tc_jira_key'],
                               "testscript": res['testscript'],
                               "ts_jira_key": res['ts_jira_key']
                            }

                   response.append(record)

        return jsonify({"response":json.loads(json_util.dumps(response))}),200

    except Exception as e:
       return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500
