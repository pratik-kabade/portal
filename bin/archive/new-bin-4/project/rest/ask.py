from flask import Blueprint, request, jsonify
from util.genesislogger import GenesisLogger
from llm import LlamaIndexManager
import json
from sklearn.metrics.pairwise import cosine_similarity
from db import DBUtil
import numpy as np

logger = GenesisLogger.get_instance()

db = "genesis"
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
    question_embedding = instance.generate_embeddings(question)

    # check for previous response
    cached_response = get_cached_positive_response(question_embedding, db, collection)
    if cached_response:
        print("Returning cached positive response.")
        return jsonify({"answer": cached_response})

    queryengine = instance.getQueryEngine(project_name)

    if queryengine is None:
        return jsonify({"answer": "No Query Engine"})

    response = queryengine.query(question)
    print("Generated response:", response)
    response = str(response)

    final_response = get_new_response_if_needed(question, question_embedding, response, queryengine, instance, db, collection)
#    final_response = str(final_response)
    return jsonify({"answer": final_response})

def train(reward, response, question_embedding):
    ex_question_embedding = np.array(question_embedding)
    records = DBUtil.get_all_records(db, collection)

    found_similar = False
    for record in records:
        stored_embedding = np.array(record.get('question_embedding'))
        similarity = cosine_similarity([stored_embedding], [ex_question_embedding])[0][0]
        if similarity > 0.9:
            print("similar record found updating with new feedback")
            record['reward'] = reward
            record['response'] = response
            record['question_embedding'] = question_embedding
            DBUtil.update_record(db, collection, record)
            found_similar = True
            break
    if not found_similar:
        record = {
            "reward": reward,
            "last_response": response,
            "question_embedding": question_embedding
        }
        DBUtil.createOrUpdate(db, collection, record)
    return

def get_cached_positive_response(question_embedding, db, collection):
    print("in cache response")
    question_embedding = np.array(question_embedding)
    records = DBUtil.get_all_records(db, collection)
    for record in records:
        stored_embedding = np.array(record.get('question_embedding'))
        similarity = cosine_similarity([stored_embedding], [question_embedding])[0][0]
        print("similarity:", similarity)
        if similarity > 0.9:
            if record.get('reward', 0) == 1:
                return record.get('last_response')
    return None

def get_new_response_if_needed(question, question_embedding, response, queryengine, instance, db, collection):
    print("in new response")
    question, question_embedding, response, queryengine, instance, db, collection
    records = DBUtil.get_all_records(db, collection)
    for record in records:
        stored_embedding =  np.array(record.get('question_embedding'))
        similarity = cosine_similarity([stored_embedding], [question_embedding])[0][0]
        if similarity > 0.9:
            if record.get('last_reward', 0) == 0 :
               # response_embedding = instance.generate_embeddings(response)
                stored_response = record.get('last_response')
#                str_response = str(response)
                better_question = (
                    f"Question: {question}\n"
                    f"Response: {response}\n"
                    "The above response is not satisfactory. please provide a more detailed, accurate, and comprehensive response by understanding the semantics and requirements of given question."
                )
                print("better_question",better_question)
                better_response = queryengine.query(better_question)
 #               print("better_response",better_response)

                better_response_embedding = instance.generate_embeddings(better_response)
                stored_response_embedding = instance.generate_embeddings(stored_response)
                similarity = cosine_similarity([better_response_embedding], [stored_response_embedding])[0][0]
                better_response = str(better_response)
                print("better_response_str", better_response)
                if similarity > 0.9:
                    print("Same negative feedback response generated, re-querying...")
                    new_response = queryengine.query(question)
                    new_response = str(new_response)
                    new_response_embedding = instance.generate_embeddings(new_response)
                    similarity_new_response = cosine_similarity([stored_response_embedding], [new_response_embedding])[0][0]
                    if similarity_new_response > 0.9:
                        print("still negative feedback response generated")
#                       response =str(response)
                        response += " (please check additional sources or context)"
                        return response
                    else:
                        print("different response generated")
#                        new_response = str(new_response)
                        return new_response
#                better_response = str(better_response)
                return better_response
#    response = str(response)
    return response

feedback_api = Blueprint('feedback_api', __name__)
@feedback_api.route('/api/feedback_api', methods=['POST'])
def feedback():
    question = request.json['question']
    instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()
    question_embedding = instance.generate_embeddings(question)
    response = request.json['answer']
    if(request.json['feedback'] == "like"):
       feedback = 1
    else:
       feedback = 0

    if feedback is not None:
        print("Feedback received:", feedback)
        train(feedback, response, question_embedding)
        print("Trained agent with feedback")

    return jsonify({"answer": "saved succesfull"})
