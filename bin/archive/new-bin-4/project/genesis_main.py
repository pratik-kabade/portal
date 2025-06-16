from flask import Flask
from flask_cors import CORS
from rest.test_bed import get_testbed_api, set_testbed_api, update_testbed_api, delete_testbed_api
from rest.ask import ask_api, feedback_api
from rest.report import report_api
from rest.execution import executescript_api
from rest.testmgmt import asktestcases_api, asktestscripts_api, testscriptoutput_api
from rest.jirasettings import getjirasettings_api, createjirasettings_api, deletejirasettings_api, create_child_jira_api, updatejira_api, createjira_api, updatechildjira_api,getjiraproject_api, getjirauserstories_api
from rest.authenticate import auth_api
from rest.docloader import getfile_api, upload_api, download_api, ingest_api
from rest.project import getproject_api, createproject_api, deleteproject_api, getProjectdata_api
from rest.userstory import getuserstory_api, createuserstory_api, deleteuserstory_api, getuserstory_prj_api,delete_tc_in_us_api
from rest.testcases import gettestcases_api, getmultipletestcases_api, getProjectData_api
from rest.dashboard import getdashboard_api, getExecutionStatus_api , getAllExecutionStatus_api, getBug_api
from util.genesislogger import GenesisLogger
from dotenv import load_dotenv
import os

#from rest.agents_testmgmt import agents_asktestcases_api
# Create Flask application
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://localhost:4200"}})

# Instantiating Logger
logger = GenesisLogger.get_instance()

# load the config file into environment variables.
load_dotenv("cfg/config.txt")


# Register blueprints for handling file-related endpoints
app.register_blueprint(set_testbed_api)
app.register_blueprint(get_testbed_api)
app.register_blueprint(update_testbed_api)
app.register_blueprint(delete_testbed_api)
app.register_blueprint(ask_api)
app.register_blueprint(feedback_api)
app.register_blueprint(getfile_api)
app.register_blueprint(report_api)
app.register_blueprint(getProjectData_api)
app.register_blueprint(upload_api)
app.register_blueprint(download_api)
app.register_blueprint(ingest_api)
app.register_blueprint(asktestcases_api)
app.register_blueprint(asktestscripts_api)
app.register_blueprint(getmultipletestcases_api)
app.register_blueprint(getBug_api)
app.register_blueprint(auth_api)
app.register_blueprint(getproject_api)
app.register_blueprint(getProjectdata_api)
app.register_blueprint(createproject_api)
app.register_blueprint(deleteproject_api)
app.register_blueprint(getuserstory_api)
app.register_blueprint(createuserstory_api)
app.register_blueprint(deleteuserstory_api)
app.register_blueprint(gettestcases_api)
app.register_blueprint(getuserstory_prj_api)
app.register_blueprint(getdashboard_api)
app.register_blueprint(getExecutionStatus_api)
app.register_blueprint(getAllExecutionStatus_api)
app.register_blueprint(executescript_api)
app.register_blueprint(delete_tc_in_us_api)
app.register_blueprint(testscriptoutput_api)


app.register_blueprint(getjiraproject_api)
app.register_blueprint(getjirauserstories_api)
app.register_blueprint(getjirasettings_api)

app.register_blueprint(createjirasettings_api)
app.register_blueprint(createjira_api)
app.register_blueprint(create_child_jira_api)
app.register_blueprint(updatejira_api)
app.register_blueprint(updatechildjira_api)
app.register_blueprint(deletejirasettings_api)


# Run the Flask application
if __name__ == '__main__':
    logger.info("Starting the Genesis applciation")
    app.run(debug=True, host=os.getenv("BACKEND_HOST"), port=os.getenv("BACKEND_PORT"))
