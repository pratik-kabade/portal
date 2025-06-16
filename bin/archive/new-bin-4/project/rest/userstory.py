from flask import Blueprint, request, jsonify
from db import DBUtil
from util.genesislogger import GenesisLogger
from datetime import datetime
import os
import random
import json
from bson import json_util
from util import jirautil

# Instantiating Logger
logger = GenesisLogger.get_instance()

db = os.getenv("MONGODB_NAME")
collection = "userstories"

getuserstory_api = Blueprint('getuserstory_api', __name__)
@getuserstory_api.route('/api/userstory/<user>', methods=['GET'])
def getUserStory(user):
    logger.debug("GET /userstory")

    try:
        filter2 = {"createdby" : user}
        result = DBUtil.getDocumentByKeyValue(db,collection,"createdby", user)
        logger.debug(result)
        response = json.loads(json_util.dumps(result))

        for res in response:
            filters = {"createdby":user, "userstory":res["_id"]}
            test_case_count = DBUtil.getDocumentCount(db, "testcases", filters)
            if test_case_count:
                res["testcasecount"] = test_case_count
            else:
                res["testcasecount"] = 0

        return jsonify({"response":json.loads(json_util.dumps(response))}),200
    except Exception as e:
        logger.error(e)
        # If an error occurs during the retrieval process, return a JSON response with an error message and status code 500 (Internal Server Error
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

getuserstory_prj_api = Blueprint('getuserstory_prj_api', __name__)
@getuserstory_prj_api.route('/api/userstory/<prj>/<user>', methods=['GET'])
def getUserStoryForProject(prj,user):
    logger.debug("GET /userstory/<prj>/<user>")

    try:
        filter = {"project":prj, "createdby" : user}
        result = DBUtil.getDocumentByMultipleKeyValue(db,collection,filter)
        logger.debug(result)
        response = json.loads(json_util.dumps(result))

        for res in response:
            filters = {"createdby":user, "userstory":res["_id"]}
            test_case_count = DBUtil.getDocumentCount(db, "testcases", filters)
            if test_case_count:
                res["testcasecount"] = test_case_count
            else:
                res["testcasecount"] = 0

        # Check if results exist
        # if not result:
           # return jsonify({"error": "No user stories found for this project and user combination"}), 404

        # Extract filename from the retrieved document
        # projectname = result.get("projectname", "")

        # Count total user stories for the project
        # project_filter = {"project": prj}  # Filter by project only
        # user_story_count = DBUtil.getDocumentCount(db, collection, project_filter)
        # current_time = datetime.utcnow().strftime("%M:%H %d-%m-%Y")

        return jsonify({"response" : response}),200
        # return jsonify({"projectname": projectname, "userStoryCount": user_story_count, "time": current_time}),200                  #({"response":json.loads(json_util.dumps(result))})
    except Exception as e:
        logger.error(e)
        # If an error occurs during the retrieval process, return a JSON response with an error message
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500


createuserstory_api = Blueprint('createuserstory_api', __name__)
@createuserstory_api.route('/api/userstory/<user>', methods=['POST'])
def createUserStory(user):
    logger.debug("POST /userstory/<user>")

    try:
        userStoryName = request.json['title']
        projectId = request.json['project']
        result = DBUtil.getDocumentByKeyValue(db,"projects","_id",projectId)
        projectname = result[0]['title']
        new_userstory = jirautil.createNewissue(userStoryName, userStoryName,"Story")
        record = {
            "_id" : str(random.randint(1,10000000)),
            "project" : projectId,
	    "projectname" : projectname,
            "jiraid" :new_userstory.split('browse/')[1],
            "title" : userStoryName,
            "createdby" : user,
            "createddate" : datetime.utcnow().strftime("%M:%H %d-%m-%Y")
            }

        DBUtil.createOrUpdate(db, collection, record)
        return jsonify({"response":"User Story added successfully"}),200
    except Exception as e:
        logger.error(e)
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

deleteuserstory_api = Blueprint('deleteuserstory_api', __name__)
@deleteuserstory_api.route('/api/userstory/<user>/<usid>', methods=['DELETE'])
def deleteUserStory(user, usid):
    logger.debug("DELETE /userstory")

    try:
        tc_filter = {"createdby" : user, "userstory" : usid}
        delcount = DBUtil.delete_document(db, "testcases", tc_filter)

        filter = {"createdby" : user, "_id" : usid}
        delcount = DBUtil.delete_document(db,collection,filter)
        if delcount == 1:
            return jsonify({"message":"delete successfull"}),200
        else:
            return jsonify({'error': 'Error deleting document,  no record found'}), 500
    except Exception as e:
        logger.error(e)
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

delete_tc_in_us_api = Blueprint('delete_tc_in_us_api', __name__)
@delete_tc_in_us_api.route('/api/userstory/tc/<user>/<tcid>', methods=['DELETE'])
def deleteTCInUserStory(user, tcid):
        logger.debug("DELETE /userstory/<TCID>")

        try:
            tc_filter = {"createdby" : user, "_id" : tcid}
            delcount = DBUtil.delete_document(db, "testcases", tc_filter)
            print (f"Deleting the test case in user story, - found ", delcount)

            if delcount == 1:
                return jsonify({"message":"Test case delete successfull"}),200
            else:
                return jsonify({'error': 'Error deleting document,  no record found'}), 500
        except Exception as e:
            logger.error(e)
            return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500
