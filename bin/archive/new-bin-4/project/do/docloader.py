from pymongo import MongoClient
from flask import Blueprint, request, jsonify, send_file

import os
import timeit
import random
import json
from bson import json_util
import datetime

from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex,Settings, load_index_from_storage, StorageContext
import os
from llm import LlamaIndexManager

instance = LlamaIndexManager.clsLlamaIndexManager.get_instance()

from db import DBUtil
from util.genesislogger import GenesisLogger

# Instantiating Logger
logger = GenesisLogger.get_instance()

db = os.getenv("MONGODB_NAME")
collection = "ragdocs"

getfile_api = Blueprint('getfile_api', __name__)
@getfile_api.route('/api/files/<user>', methods=['GET'])
def get_files(user):
    logger.debug("in get_files")

    """Retrieve files metadata from MongoDB and return as JSON."""
    try:
        # Retrieve metadata of all files from the MongoDB collection
        metadata = DBUtil.getDocumentByKeyValue(db, collection, "user", user)
        return jsonify(metadata), 200

    except Exception as e:
        logger.error(e)
        # If an error occurs during the retrieval process, return a JSON response with an error message and status code 500 (Internal Server Error
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

# Create a blueprint for handling file upload endpoint
upload_api = Blueprint('upload_api', __name__)
@upload_api.route('/api/upload/<user>/<projectName>', methods=['POST'])
def upload_file(user,projectName):

    logger.debug("in Upload_file")
    project_path = os.path.join(os.getenv("DATA_PATH"),projectName)

    """Handle file upload and store in folder and MongoDB."""
    # Check if the 'file' part is present in the request
    try:
        if 'file' not in request.files:
           return jsonify({'error': 'No file part in the request!'}), 400

        file = request.files['file']
        # Check if a file was selected for uploading
        if file.filename == '':
           return jsonify({'error': 'No file selected for uploading!'}), 400

    except Exception as e:
        print(e)
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500


    # Check if the selected file has an allowed file extension
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(project_path, filename)

        # Save the file to the specified upload folder
        file.save(file_path)

        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Create metadata for the uploaded file
            random_number = random.randint(1, 100000)
            metadata = {
                '_id': str(random_number),
                'document': filename,
                'projectName': projectName,
                'version': '1.0',
                'date': datetime.datetime.utcnow(),
                'status': 'uploaded',
                'user': 'admin'
            }

            # Insert metadata into MongoDB collection
            DBUtil.createOrUpdate(db, collection, metadata)

            # Return success message along with file ID as JSON response
            return jsonify({'message': 'File uploaded and stored successfully!'}), 200
        except Exception as e:
            logger.error(e)
            # If an error occurs while storing the file, delete the file and return an error message
            os.remove(file_path)
            return jsonify({'error': f'Error storing file: {str(e)}'}), 500
    else:
        # If the file type is not allowed, return an error message
        return jsonify({'error': 'File type not allowed!'}), 400

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in os.getenv("DOCUMENT_TYPE")

# endpoints/download.py
# Create a blueprint for handling file download endpoint
download_api = Blueprint('download_api', __name__)
@download_api.route('/api/download/<user>/<projectName>/<filename>', methods=['GET'])
def download_file(user, projectName, filename):
    logger.debug("in download_file")
    """Handle file download."""
    try:
        # Construct the file path
        file_path = os.path.join(os.getenv("DATA_PATH"), projectName, filename)

        # Check if the file exists
        if os.path.exists(file_path):

            # If the file exists, create a response with the file as an attachment
            response = send_file(file_path, as_attachment=True)

            # Set the response header to specify the content type
            response.headers['Content-Type'] = 'application/octet-stream'
            return response
        else:

            # If the file does not exist, return a JSON response with an error message
            return jsonify({'error': 'File not found!'}), 404
    except Exception as e:
        # If an error occurs during the download process, return a JSON response with an error message
        logger.error(e)
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

# Create a blueprint for handling file ingest endpoint
ingest_api = Blueprint('ingest_api', __name__)

@ingest_api.route('/api/ingest/<user>/<projectName>/<fileName>', methods=['POST'])
def ingest_file(user, projectName, fileName):
  logger.debug("in ingest_file")
  try:

    # Call the run_ingest function from document_processing.text_processing to process the file
    instance.run_ingest(fileName, projectName)

    # Update metadata status to 'ingested'
    filter = {"projectName" : projectName, "document" : fileName}
    resdata = DBUtil.getDocumentByMultipleKeyValue(db,collection,filter)
    metadata = {
                '_id': resdata[0].get("_id"),
                'document': resdata[0].get("document"),
                'projectName': resdata[0].get("projectName"),
                'version': resdata[0].get("version"),
                'date': datetime.datetime.utcnow(),
                'status': 'Ingested',
                'user': 'admin'
    }
    DBUtil.createOrUpdate(db, collection, metadata)
    return jsonify({'message': 'File ingestion and chunking started successfully!'}), 200
  except Exception as e:
    logger.error(e)
    return jsonify({'error': f'Error ingesting file: {str(e)}'}), 500


