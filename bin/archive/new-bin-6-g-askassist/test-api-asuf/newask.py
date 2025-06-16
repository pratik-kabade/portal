from flask import Blueprint, request, jsonify
from util.genesislogger import GenesisLogger
from llm import LlamaIndexManager
import json
from sklearn.metrics.pairwise import cosine_similarity
from db import DBUtil
import numpy as np
import random
from datetime import datetime
import os
import requests
from util.jirautil import get_userstories

logger = GenesisLogger.get_instance()

db = "genesis_dev"
collection = "Rl_data"

# Create a Blueprint for handling questions and answers
ask_api = Blueprint('ask_api', __name__)
@ask_api.route('/api/ask', methods=['POST'])
def ask():
    # Handle general questions and return answers.
    data = request.json
    question = data.get('question', "")
    project_name = data.get('project_name', "")
    feedback = request.json.get('feedback', None)
    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()

    #queryengine = instance.getQueryEngine(project_name)
    queryengine = instance.getChatEngine(project_name)
    if queryengine is None:
        return jsonify({"answer": "No Query Engine"})

    response = queryengine.chat(question)
    response = str(response)

    return response
    # return jsonify({"answer": response})

# curl -X POST -H "Content-Type: application/json" -d '{"question" : "give me all the context present here", "project_name" : "ASUF"}' http://localhost:5000/api/ask
# curl -X POST -H "Content-Type: application/json" -d '{"question" : "give me all the list of the get put post delete routes mentioned here and also give me steps to test that route do that for all the routes", "project_name" : "ASUF"}' http://localhost:5000/api/ask

# curl -X POST -H "Content-Type: application/json" -d '{"question" : "hi", "project_name" : "RDKB"}' http://localhost:5000/api/feedback_api

feedback_api = Blueprint('feedback_api', __name__)
@feedback_api.route('/api/feedback_api', methods=['POST'])
def feedback():
    try:
        # projectName = request.json['title']
        # projectDesc = request.json['description']
        # jiraProjectKey = request.json['jiraProjectKey']
        # jiraProjectName = request.json['jiraProjectName']

        projectName = 'ASUF'
        projectDesc = 'testing api'
        jiraProjectKey = 'RDKB'
        jiraProjectName = 'RDK Broadband'

        user = 'admin'

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

        url = "https://raw.githubusercontent.com/jdegre/5GC_APIs/master/TS29509_Nausf_UEAuthentication.yaml"
        query_parameters = {"downloadformat": "txt"}
        res = requests.get(url, params=query_parameters)
        FNAME = 'asuf.txt'
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



# def train(reward, response, question_embedding):
#     ex_question_embedding = np.array(question_embedding)
#     records = DBUtil.get_all_records(db, collection)

#     found_similar = False
#     for record in records:
#         stored_embedding = np.array(record.get('question_embedding'))
#         similarity = cosine_similarity([stored_embedding], [ex_question_embedding])[0][0]
#         if similarity > 0.9:
#             print("similar record found updating with new feedback")
#             record['reward'] = reward
#             record['response'] = response
#             record['question_embedding'] = question_embedding
#             DBUtil.update_record(db, collection, record)
#             found_similar = True
#             break
#     if not found_similar:
#         record = {
#             "reward": reward,
#             "last_response": response,
#             "question_embedding": question_embedding
#         }
#         DBUtil.createOrUpdate(db, collection, record)
#     return

# def get_cached_positive_response(question_embedding, db, collection):
#     question_embedding = np.array(question_embedding)
#     records = DBUtil.get_all_records(db, collection)
#     for record in records:
#         stored_embedding = np.array(record.get('question_embedding'))
#         similarity = cosine_similarity([stored_embedding], [question_embedding])[0][0]
#         print("similarity:", similarity)
#         if similarity > 0.9:
#             if record.get('reward', 0) == 1:
#                 return record.get('last_response')
#     return None

# def get_new_response_if_needed(question, question_embedding, response, queryengine, instance, db, collection):
#     records = DBUtil.get_all_records(db, collection)
#     for record in records:
#         stored_embedding =  np.array(record.get('question_embedding'))
#         similarity = cosine_similarity([stored_embedding], [question_embedding])[0][0]
#         if similarity > 0.9:
#             if record.get('last_reward', 0) == 0 :
#                 stored_response = record.get('last_response')
#                 better_question = (
#                     f"Question: {question}\n"
#                     f"Response: {response}\n"
#                     "The above response is not satisfactory. please provide a more detailed, accurate, and comprehensive response by understanding the semantics and requirements of given question."
#                 )
#                 better_response = queryengine.query(better_question)
#                 better_response = str(better_response)
#                 better_response_embedding = instance.generate_embeddings(better_response)
#                 stored_response_embedding = instance.generate_embeddings(stored_response)
#                 similarity = cosine_similarity([better_response_embedding], [stored_response_embedding])[0][0]
#                 better_response = str(better_response)
#                 if similarity > 0.9:
#                     better_response += " (please check additional sources or context)"
#                     return better_response
#                 return better_response
#     return response

# '''
# def get_new_response_if_needed(question, question_embedding, response, queryengine, instance, db, collection):
#     question, question_embedding, response, queryengine, instance, db, collection
#     records = DBUtil.get_all_records(db, collection)
#     for record in records:
#         stored_embedding =  np.array(record.get('question_embedding'))
#         similarity = cosine_similarity([stored_embedding], [question_embedding])[0][0]
#         if similarity > 0.9:
#             if record.get('last_reward', 0) == 0 :
#                 response_embedding = instance.generate_embeddings(response)
#                 stored_response = record.get('last_response')
#                 stored_response_embedding = instance.generate_embeddings(stored_response)
#                 similarity = cosine_similarity([response_embedding], [stored_response_embedding])[0][0]
#                 if similarity > 0.9:
#                     print("Same negative feedback response generated, re-querying...")
#                     new_response = queryengine.query(question)
#                     new_response = str(new_response)
#                     new_response_embedding = instance.generate_embeddings(new_response)
#                     similarity_new_response = cosine_similarity([stored_response_embedding], [new_response_embedding])[0][0]
#                     if similarity_new_response > 0.9:
#                         print("still negative feedback response generated")
#  #                       response =str(response)
#                         response += " (please check additional sources or context)"
#                         return response
#                     else:
#                         print("different response generated")
# #                        new_response = str(new_response)
#                         return new_response
# #                new_response = str(new_response)
#                 return new_response
# #    response = str(response)
#     return response
# '''

# feedback_api = Blueprint('feedback_api', __name__)
# @feedback_api.route('/api/feedback_api', methods=['POST'])
# def feedback():
#     question = request.json['question']
#     instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
#     question_embedding = instance.generate_embeddings(question)
#     response = request.json['answer']
#     if(request.json['feedback'] == "like"):
#        feedback = 1
#     else:
#        feedback = 0

#     if feedback is not None:
#         print("Feedback received:", feedback)
#         train(feedback, response, question_embedding)
#         print("Trained agent with feedback")

#     return jsonify({"answer": "saved succesfull"})
