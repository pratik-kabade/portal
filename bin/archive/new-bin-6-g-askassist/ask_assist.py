from flask import Blueprint, request, jsonify
from util.genesislogger import GenesisLogger
from llm import LlamaIndexManager
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
import json
import os
from db import DBUtil
from rest.prompts import myprompts
from util.jirautil import fetchDetails

logger = GenesisLogger.get_instance()
db = os.getenv("MONGODB_NAME")

ask_assist = Blueprint('ask_assist', __name__)
@ask_assist.route('/api/ask_assist/<user>', methods=['POST'])
def ask(user):
    id = request.json
    filter = { "createdby" : user, "CustId" : id }
    result = DBUtil.getDocumentByKeyValue(db, "Customers", filter)
    response = json.loads(json_util.dumps(result))

    return jsonify({ "response" : response[0] })













'''
def categorize_issue(issue):
    Settings.llm = Ollama(model="llama3:latest", request_timeout=60.0, temperature=0)
    llm = Settings.llm
    mainPrompt = "[INST]\n" + myprompts.prompt_persona + "\n\n" + myprompts.field_persona + "\n[/INST]\n" + "<<<issue>>>\n" + issue
    response = llm.complete(mainPrompt)
    category = response
    return category

# Create a Blueprint for handling questions and answers
ask_assist = Blueprint('ask_assist', __name__)
@ask_assist.route('/api/ask_assist', methods=['POST'])
def ask():
    # Handle general questions and return answers.
    data = request.json
    question = data.get('question', "")
    project_name = data.get('project', "")
    category = categorize_issue(question)
    print(category)
    category = str(category)
    return jsonify({'category':category})
'''

# Create a Blueprint for handling replying on service down
assist_service = Blueprint('assist_service',__name__)
@assist_service.route('/api/assist_service', methods=['POST'])
def service_down():
    data = request.get_json()
    step = data.get('step', "")

    if step == 'category':
        category = data.get('category', "")

        if category == 'ServiceDown':
            return jsonify({"message": "Please provide your zip code."})

    if step == 'zip_code':
        zip_code = data.get('zip_code', "")
        project_name = data.get('project',"")
        instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
        chat_engine = instance.getChatEngine(project_name)
        # Assuming no project-specific engine
        if chat_engine is None:
            return jsonify({"answer": "No Query Engine"})
        #prompt_persona = 'Check in the embedding database, if there is an issue with matching zipcode after the format <#ZIPCODE> in section "Impacted Zip code". Return Resolution time if there is a match.'
        prompt_persona = "check in the embedding database, if there is any issue which contains the zipcode after the format <#ZIPCODE> in section 'Impacted Zip code'. Return Resolution time if you find one. /n please provide the response in yes or no format only"
        question = f"<#ZIPCODE> {zip_code}"
        mainPrompt = prompt_persona  + question
        print(mainPrompt)
        response = chat_engine.chat(mainPrompt)
        response = str(response).lower()
        print(response)
        if "yes" in response:
            return jsonify({"message": "Yes, you area is impacted. Estimated time of resolution is 2hr. Do you want to open a ticket?"})
        else:
            return jsonify({"message" : "No, You  area is not impacted. Do you want to open a ticket?"})


# Create a Blueprint for handling replying on service down
assist_general = Blueprint('assist_general', __name__)
@assist_general.route('/api/assist_general', methods=['POST'])
def assist_general_fn():
    print ("In General Help")
    data = request.get_json()
    step = data.get('step', "")
    if step == 'category':
        category = data.get('category', "")
        category = category.lower()
        category = category.strip()
        if category == 'generalhelp' or category == 'general help':
            return jsonify({"message": "Please provide the details of the issue or provide the jira id"})
    if step == 'question':
        project_name = data.get('project',"")
        question = data.get('question', "")
        #res = check_jira(project_name, question)
        #print("res        ", res)
        instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
        chat_engine = instance.getChatEngine(project_name)
        if chat_engine is None:
            return jsonify({"message": "No Query Engine"})

        # response = chat_engine.chat(res)
        response = chat_engine.chat(question)
        response = str(response)
        print(response)
        return jsonify({"message": response})

    return jsonify({"message" : "No, there is no resolution found for this issue. Do you want to open a ticket?"})


def check_jira(project_name, prompt):
    id_prompt=f'Check if the prompt after tag ##PROMPT## has any ID in alphanumneric format for example RDKB-123. If yes, then return only the id in capital letters. If the prompt does not have any id in above format then return word "False" ##PROMPT## {prompt}'
    print (f"Input Prompt : {id_prompt}")

    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
    queryengine = instance.getQueryEngine(project_name)

    if queryengine is None:
        return jsonify({"answer": "No Query Engine"})

    id = str(queryengine.query(id_prompt))
    print (f"Return ID : {id}")
    #id = str(queryengine.chat(id_prompt))

    if id == 'False':
        print("Could not find the JIRA from the Prompt. Returning prompt as-is")
        return prompt
    else:
        print(f"Found the JIRA from the Prompt. {id}")
        jira_content = fetchDetails(id)
        q = f'Using the content from the tag ##JIRA_Content##, answer the prompt after the tag ##Prompt##. \n\n ##JIRA_ Content##: {jira_content}, \n\n ##Prompt##: {prompt}.'
        #q = f'From {jira_content}, \n\n Answer this {prompt} Please provide the answer clearly.'

        return q
