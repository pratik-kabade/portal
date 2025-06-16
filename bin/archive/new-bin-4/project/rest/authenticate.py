from flask import Blueprint, request, jsonify
from db import DBUtil
from util.genesislogger import GenesisLogger
import os

# Instantiating Logger
logger = GenesisLogger.get_instance()

db = os.getenv("MONGODB_NAME")
collection = "users"


auth_api = Blueprint('auth_api', __name__)
@auth_api.route('/auth', methods=['POST'])
def authenticate():
    logger.debug("Authenticate API call")

    try:
       user = request.json['user']
       password = request.json['password']

       response = DBUtil.getDocumentByKeyValue(db, collection, "username", user)
       _password = response[0].get("password")
   
       if password == _password:
          return jsonify({"result":"success"}),200
       else:
          return jsonify({"result":"Either user or password is not correct."}),401
    except Exception as e:
       logger.error(e)
       return jsonify({"result":"Inernal Server Error: {str(e)}"}),500



