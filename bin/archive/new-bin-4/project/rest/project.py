from flask import Blueprint, request, jsonify
from db import DBUtil
from util.genesislogger import GenesisLogger
from datetime import datetime
import os
from bson import json_util
import json
import random
import requests
from llm import LlamaIndexManager
from util.jirautil import get_userstories
# Instantiating Logger
logger = GenesisLogger.get_instance()

db = os.getenv("MONGODB_NAME")
collection = "projects"
userstory_collection = "userstories"

# curl -X GET "http://localhost:5000/api/projects/admin"

getproject_api = Blueprint('getproject_api', __name__)
@getproject_api.route('/api/projects/<user>', methods=['GET'])
def getProjects(user):
    logger.debug("GET API: Projects")

    try:
        filter2 = {"createdby" : user}
        result = DBUtil.getDocumentByKeyValue(db,collection,"createdby",user)
        logger.debug(result)
        response = json.loads(json_util.dumps(result))

        for res in response:
            userstories = DBUtil.getDocumentByKeyValue(db,"userstories","project", res["_id"])
            storycount = len(userstories)
            res["userstorycount"] = str(storycount)

        return jsonify({"response":json.loads(json_util.dumps(response))}),200
    except Exception as e:
        logger.error(e)
        # If an error occurs during the retrieval process, return a JSON response with an error message and status code 500 (Internal Server Error
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

getProjectdata_api = Blueprint('getProjectdata_api', __name__)
@getProjectdata_api.route('/api/projects/<user>/<_id>', methods=['GET'])
def getProjectdata(user,_id):
    logger.debug("GET /Projects")
    try:
        filter = {"createdby" : user, "_id":_id}
        projects = DBUtil.getDocumentByMultipleKeyValue(db,collection,filter)
        final_response = []
        for project in projects:
            userstories = DBUtil.getDocumentByKeyValue(db,"userstories","project", project["_id"])
            for userstory in userstories:
                response = {
                  "_id" : str(random.randint(1, 100000)),
                  "projectName": project["title"],
                  "description": project["description"],
                  "createdby": user,
                  "createddate": datetime.utcnow(),
                  "userstory": userstory["title"],
                  "testcases": [],
	          "testscripts":[],
                }
                filter = {"createdby" : user,"userstory":userstory["_id"]}
                testcases = DBUtil.getDocumentByMultipleKeyValue(db,"testcases",filter)
                for testcase in testcases:
                    response["testcases"].append({"testcase": testcase["testcase"], "tc_jira": testcase["tc_jira"]})
                    response["testscripts"].append({"testscript": testcase["testscript"], "ts_jira": testcase["ts_jira"], "language": testcase["language"]})

                final_response.append(response)
        return jsonify({"response":json.loads(json_util.dumps(final_response))}),200

    except Exception as e:
        logger.error(e)
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

createproject_api = Blueprint('createproject_api', __name__)
@createproject_api.route('/api/projects/<user>', methods=['POST'])
def createProject(user):
    logger.debug("POST /projects")
    try:
        projectName = request.json['title']
        projectDesc = request.json['description']
        jiraProjectKey = request.json['jiraProjectKey']
        jiraProjectName = request.json['jiraProjectName']

        projectId = str(random.randint(1, 100000))
        prjRecord = {
            "_id" : projectId,
            "title" : projectName,
            "description" : projectDesc,
            "jiraprojectKey" : jiraProjectKey,
            "jiraprojectName" : jiraProjectName,
            "createdby" : user,
            "createddate" : datetime.utcnow()
            }
        DBUtil.createOrUpdate(db, collection, prjRecord)

        # Create data directory path for documents to upload.
        path = os.path.join(os.getenv("DATA_PATH"), projectName)
        if not os.path.exists(path):
           os.mkdir(path)

        url = "https://raw.githubusercontent.com/pratik-kabade/bin/main/sample.pdf"
        query_parameters = {"downloadformat": "pdf"}
        res = requests.get(url, params=query_parameters)
        FNAME = 'sample.pdf'
        DIR = os.path.join("data/",projectName,FNAME)

        with open(DIR, "wb") as file:
            file.write(res.content)
            print("file saved")
        print("file next")
        llama_index_manager = LlamaIndexManager.clsLlamaIndexManager.get_instance()
        llama_index_manager.run_ingest(FNAME, projectName)

        # pull user stories for this project from JIRA and add in DB.
        if jiraProjectKey != "None":
           userstories = get_userstories(jiraProjectKey)

           for story in userstories:
               record = {
                   "_id" : str(random.randint(1,10000000)),
                   "project" : projectId,
                   "projectname" : projectName,
                   "jiraid" : story['key'],
                   "title" : story['title'],
                   "createdby" : user,
                   "createddate" : datetime.utcnow().strftime("%M:%H %d-%m-%Y")
                   }
               DBUtil.createOrUpdate(db, "userstories", record)

        return jsonify({"response" : "Project create sucessfull"}), 200
    except Exception as e:
        logger.error(e)
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

deleteproject_api = Blueprint('deleteproject_api', __name__)
@deleteproject_api.route('/api/projects/<user>/<_id>', methods=['DELETE'])
def deleteProject(user, _id):
    logger.debug("DELETE /project")
    try:
        tc_filter = {"project": _id, "createdby":user}
        delcount = DBUtil.delete_document(db,"testcases",tc_filter)

        us_filter = {"project": _id, "createdby" : user}
        delcount = DBUtil.delete_document(db,"userstories",us_filter)

        prj_filter = {"_id": _id, "createdby": user}
        delcount = DBUtil.delete_document(db,collection,prj_filter)
        if delcount == 1:
            return jsonify({"message":"delete successfull"}),200
        else:
            return jsonify({'error': 'Error deleting document,  no record found'}), 500
    except Exception as e:
        logger.error(e)
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500
