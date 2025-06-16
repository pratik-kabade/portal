from datetime import datetime
import os
from flask import Blueprint, request, jsonify
from db import DBUtil
from util.genesislogger import GenesisLogger

logger = GenesisLogger.get_instance()
db = os.getenv("MONGODB_NAME")
collection = "testcases"

report_api = Blueprint('report_api', __name__)
@report_api.route('/api/report/<user>', methods=['POST'])
def generateReport(user):
    project = request.json["project"]
    status = request.json["status"]
    startDate = request.json["startDate"]
    endDate = request.json["endDate"]

    startDate = datetime.fromisoformat(startDate.replace("Z", "+00:00"))
    startDate = startDate.strftime("%Y-%m-%d %H:%M:%S.%f")
    endDate = datetime.fromisoformat(endDate.replace("Z", "+00:00"))
    endDate = endDate.strftime("%Y-%m-%d %H:%M:%S.%f")

    filter = { "createddate": {"$gte": startDate, "$lt": endDate}, "createdby": user, "project": project, "testScriptStatus": status }

    testcases = DBUtil.getDocumentByMultipleKeyValue(db, collection, filter)

    return jsonify({"response" : testcases}), 200
