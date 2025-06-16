from flask import Blueprint, request, jsonify
from util.genesislogger import GenesisLogger
from llm import LlamaIndexManager
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
import json
from db import DBUtil
from rest.prompts import myprompts

logger = GenesisLogger.get_instance()

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
    print("in ask_assist")
    data = request.json
    question = data.get('question', "")
    project_name = data.get('project', "")
    category = categorize_issue(question)
    print(category)
    category = str(category)
    return jsonify({'category':category})

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
    data = request.get_json()
    step = data.get('step', "")

    if step == 'category':
        category = data.get('category', "")

        if category == 'generalhelp':
            return jsonify({"message": "Please provide the details of the issue"})

    if step == 'question':
        project_name = data.get('project',"")
        question = data.get('question', "")
        instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
        chat_engine = instance.getChatEngine(project_name)
        # Assuming no project-specific engine
        if chat_engine is None:
            return jsonify({"answer": "No Query Engine"})
        # prompt_persona = "check in the embedding database, if you know something related to this QUESTION, \n"
        # mainPrompt = prompt_persona  + question
        response = chat_engine.chat(question)
        return jsonify(str(response))


    if step == 'create_ticket':
        bool = data.get('bool', "")
        # response = chat_engine.chat(mainPrompt)
        if "yes" in bool:
            return jsonify({"message": "Do you want to open a ticket?"})
        else:
            return jsonify({"message" : "No, there is no resolution found for this issue. Do you want to open a ticket?"})

    



'''
    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
    chat_engine = instance.getChatEngine(project_name)

    if chat_engine is None:
        return jsonify({"answer": "No Query Engine"})
    #response =   chat_engine.reset()
    response = chat_engine.chat(question)
    #response = chat_engine.stream_chat(question)
    response = str(response)
    print(f"response: {response}")

    return jsonify({"answer": response})

categorize_ask = Blueprint('categorize_ask', __name__)
@app.route('/categorize', methods=['POST'])
def categorize_issue():
    issue = request.json.get('issue')
    if not issue:
        return jsonify({'error': 'Issue is required'}), 400
    Settings.llm = Ollama(model="llama3:latest", request_timeout=60.0, temperature=0)
    llm = Settings.llm
    mainPrompt = "[INST]\n" + myprompts.prompt_persona + "\n\n" + myprompts.field_persona + "\n[/INST]\n" + "<<<issue>>>\n" + issue
    response = llm.complete(mainPrompt)
    category = response.strip()
    category = request.json.get('category')
    if not category:
        return jsonify({'error': 'Category is required'}), 400

    if 'ServiceDown' in category:
        followup = "Please provide your ZIP code."
    elif 'GeneralHelp' in category:
        followup = "Please provide more details about the issue."
    else:
        return jsonify({'error': 'Invalid category'}), 400

    return jsonify({'category': category,'followup': followup})
'''

