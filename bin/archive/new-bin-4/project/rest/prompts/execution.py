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
from util import testtojson
from db import DBUtil
import time
from rest.project import getProjects


db = os.getenv("MONGODB_NAME")
collection = "testcases"

# Instantiating Logger
logger = GenesisLogger.get_instance()

executescript_api = Blueprint('executescriptapi', __name__)
@executescript_api.route('/api/execute', methods=['POST'])
def executeScript():
    projectID = request.json['project']
    result = DBUtil.getDocumentByKeyValue(db,"projects","_id",projectID)
    projectname = result[0]['title'].lower()
    script_content = request.json["script_content"]
    #if projectname == "rdk-b":
    if "rdk" in projectname:
        script_result = executeScriptRDK(script_content)
    elif projectname == "cisco":
        script_result = executeScriptCisco(script_content)
    else:
        script_result = {"status": "fail", "output": "Unsupported project name"}
    return jsonify(script_result)


def executeScriptRDK(script_content):
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
        print("exit_code",exit_code)
        if exit_code == 0:
            if "error" in output.lower() or "exception" in output.lower() or "traceback" in output.lower() or "can't find" in output.lower():
                return_dict = {"status": "fail", "output": output}
            else:
                return_dict = {"status": "pass", "output": output}
        else:
            return_dict = {"status": "fail", "output": output}
        return return_dict
    except FileNotFoundError:
       return jsonify({"status": "fail","output": "Error executing script"}), 502
    except Exception as e:
       logger.error(str(e))
       return jsonify({"status": "fail","output": "Internal server error"}), 503

def generate_randomscript_name():
    return f"{os.urandom(8).hex()}.py"

def executeScriptCisco(script_content):
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
        print("exit_code",exit_code)
        if exit_code == 0:
            if "error" in output.lower() or "exception" in output.lower() or "traceback" in output.lower() or "can't find" in output.lower():
                return_dict = {"status": "fail", "output": output}
            else:
                return_dict = {"status": "pass", "output": output}
        else:
            return_dict = {"status": "fail", "output": output}
        return return_dict
    except FileNotFoundError:
        return jsonify({"status": "fail","output": "Error executing script"}), 502
    except Exception as e:
        logger.error(str(e))
        return jsonify({"status": "fail","output": "Internal server error"}), 503

def generate_randomscript_name():
    return f"{os.urandom(8).hex()}.py"
