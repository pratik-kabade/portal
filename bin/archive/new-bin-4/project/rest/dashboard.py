from flask import Blueprint, request, jsonify
from db import DBUtil
from util import jirautil
from util.genesislogger import GenesisLogger
import os
from bson import json_util
import json

# Instantiating Logger
logger = GenesisLogger.get_instance()

db = os.getenv("MONGODB_NAME")

getdashboard_api = Blueprint('getdashboard_api', __name__)
@getdashboard_api.route('/api/dashboard/<user>', methods=['GET'])
def getdashboard(user):
    logger.debug("GET API: Dashboard")

    try:
        filter2 = {"createdby" : user}
        prjCount = DBUtil.getDocumentCount(db,"projects",filter2)
        usCount = DBUtil.getDocumentCount(db,"userstories",filter2)
        tcCount = DBUtil.getDocumentCount(db,"testcases",filter2)

        resp = []
        resp.append({"project":prjCount, "userstory":usCount, "testcases":tcCount})
        response = {"project":prjCount, "userstory":usCount, "testcases":tcCount}
        logger.debug(resp)

        return json.loads(json_util.dumps(response)),200
    except Exception as e:
        print (e)
        logger.error(e)
        # If an error occurs during the retrieval process, return a JSON response with an error message and status code 500 (Internal Server Error
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

getExecutionStatus_api = Blueprint('getExecutionStatus_api', __name__)
@getExecutionStatus_api.route('/api/executionStatus/<user>', methods=['GET'])
def get_execution_status(user):
    #filter = { "createdby"  user }
    projects = DBUtil.getDocumentByKeyValue(db, "projects","createdby", user)
    record = []
    for project in projects:
        failFilter = { "createdby": user, "project": project['_id'], "testScriptStatus": "Failed"}
        passFilter = { "createdby": user, "project": project['_id'], "testScriptStatus": "Passed"}
        notExecutedFilter = { "createdby": user, "project": project['_id'], "testScriptStatus": "Not Executed"}
        fail = DBUtil.getDocumentByMultipleKeyValue(db, "testcases", failFilter)
        Pass = DBUtil.getDocumentByMultipleKeyValue(db, "testcases", passFilter)
        notExecuted = DBUtil.getDocumentByMultipleKeyValue(db, "testcases", notExecutedFilter)

        record.append({
                       "name": project['title'],
                       "fail": len(fail),
                       "pass": len(Pass),
                       "not_executed": len(notExecuted)
                   })

    return jsonify(record)


getAllExecutionStatus_api = Blueprint('getAllExecutionStatus_api', __name__)
@getAllExecutionStatus_api.route('/api/allExecutionStatus/<user>', methods=['GET'])
def get_allexecution_status(user):
      failFilter = { "createdby": user, "testScriptStatus": "Failed"}
      passFilter = { "createdby": user, "testScriptStatus": "Passed"}
      notExecutedFilter = { "createdby": user, "testScriptStatus": "Not Executed"}
      fail = DBUtil.getDocumentByMultipleKeyValue(db, "testcases", failFilter)
      Pass = DBUtil.getDocumentByMultipleKeyValue(db, "testcases", passFilter)
      notExecuted = DBUtil.getDocumentByMultipleKeyValue(db, "testcases", notExecutedFilter)
      record =  {
                   "fail" : len(fail),
                   "pass": len(Pass),
                   "not executed": len(notExecuted)
                }

      return jsonify(record)

getBug_api = Blueprint('getBug_api', __name__)
@getBug_api.route('/api/bug/<user>', methods=['GET'])
def get_bug(user):
     projects = DBUtil.getDocumentByKeyValue(db, "projects", "createdby", user)
     result = jirautil.getBugsStatus(projects)

     return jsonify(result)

