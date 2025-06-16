from flask import Blueprint, request, jsonify
from util.genesislogger import GenesisLogger
from db import DBUtil
import random
from datetime import datetime

db = "genesis_dev"
collection = 'test_bed'

#Create
set_testbed_api = Blueprint('set_testbed_api', __name__)
@set_testbed_api.route('/api/testbed/<user>', methods=['POST'])
def testBed(user):
    data = request.json
    name = data.get("name", "")
    description = data.get("description", "")
    port = data.get("port", "")
    hostname = data.get("hostname", "")
    username = data.get("username", "")
    password = data.get("password", "")
    devicetype = data.get("devicetype", "")

    record = {
        "_id": str(random.randint(1, 100000)),
        "createdby": user,
        "name": name,
	"description": description,
        "port": port,
        "hostname": hostname,
        "username": username,
        "password": password,
        "devicetype": devicetype,
        "time_stamp": datetime.utcnow()
    }

    DBUtil.createOrUpdate(db, collection, record)
    return jsonify({"message": "Data Updated successfully!"})

#Update
update_testbed_api = Blueprint('update_testbed_api', __name__)
@update_testbed_api.route('/api/testbed/<user>/<id>', methods=['PUT'])
def updateTestBed(user, id):
    data = request.json
    name = data.get("name", "")
    description = data.get("description", "")
    port = data.get("port", "")
    hostname = data.get("hostname", "")
    username = data.get("username", "")
    password = data.get("password", "")
    devicetype = data.get("devicetype", "")

    update_document = {
        "_id": id,
        "createdby": user,
        "name": name,
        "description": description,
        "port": port,
        "hostname": hostname,
        "username": username,
        "password": password,
        "devicetype": devicetype,
        "time_stamp": datetime.utcnow()
    }
    DBUtil.createOrUpdate(db, collection, update_document)
    return jsonify({"message" : "Data updated successfully"})

#get
get_testbed_api = Blueprint('get_testbed_api', __name__)
@get_testbed_api.route('/api/testbed/<user>', methods=['GET'])
def getTestBed(user):
    data = DBUtil.getDocumentByKeyValue(db, collection, "createdby", user)
    return jsonify(data)

#delete
delete_testbed_api = Blueprint('delete_testbed_api', __name__)
@delete_testbed_api.route('/api/testbed/<user>/<id>', methods=['DELETE'])
def deleteTestBed(user, id):
    DBUtil.delete_document_by_id(db, collection, id)
    return jsonify({"message": "Data Deleted successfully!"})

