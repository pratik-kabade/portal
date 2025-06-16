# from asyncio.windows_events import NULL
from project.db import MongoManager
from project.util.genesislogger import GenesisLogger
import os

# Instantiating Logger
logger = GenesisLogger.get_instance()


def getDbConnection():
    ## Create connection pool with 
    try:
        dbInstance = MongoManager.MongoManager.get_instance()
        return dbInstance.get_connection()
    except Exception as e:
        #print (e)
        raise e

def releaseDbConnection(connection):
    ## Create connection pool with 
    dbInstance = MongoManager.MongoManager.get_instance()
    dbInstance.release_connection(connection)

def createOrUpdate(database_name, collection_name, document):
    
    try:
        connection = getDbConnection()
        database = connection[str(database_name)]
        collection = database[collection_name]
    except Exception as dbex:
        releaseDbConnection(connection)

    existing_doc = None
    try:
        if "_id" in document:
            filter = {"_id": str(document["_id"])}
            existing_doc = collection.find_one(filter)
    except Exception as ee:
        releaseDbConnection(connection)
        raise Exception (ee.__cause__) from e
    
    try:
        # Update the document if it exists, otherwise insert a new one
        if existing_doc:
            update_result = collection.update_one(filter, {"$set": document})
        else:
            insert_result = collection.insert_one(document)

        # Return the result (update count or inserted document ID)
        releaseDbConnection(connection)
        if existing_doc:
            return update_result.matched_count  # Number of documents matched for update
        else:
            return insert_result.inserted_id
    except Exception as e:
        releaseDbConnection(connection)
        raise Exception (e.__cause__) from e
    
## Method getDocumentByID to fetch existing documents 
def getDocumentByID(database_name, collection_name, _id):
    connection = getDbConnection()
    database = connection[database_name]
    collection = database[collection_name]
    filter = {"_id": _id}
    document = collection.find_one(filter)
    
    releaseDbConnection(connection)
    if document:
        return document
    else:
        return NULL
    
## Method to search for document which has provided key value pair.
## it returns all the documents with this key value pair.    
def getDocumentByKeyValue(database_name, collection_name, search_field, search_value):
  # Connect to the database
  connection = getDbConnection()
  database = connection[str(database_name)]
  collection = database[collection_name]

  # Create a filter based on the provided search field and value
  filter = {search_field: search_value}

  # Find documents matching the filter criteria
  cursor = collection.find(filter)
  
  # Convert the cursor to a list of documents
  documents = list(cursor)
  releaseDbConnection(connection)

  return documents

## Method to search for document which has provided key value pair.
## it returns all the documents with this key value pair.
def getDocumentByMultipleKeyValue(database_name, collection_name, filters):
  """Searches for documents in a collection based on a field and value."""
  # Connect to the database
  connection = getDbConnection()
  database = connection[str(database_name)]
  collection = database[collection_name]

  # Find documents matching the filter criteria
  cursor = collection.find(filters)

  # Convert the cursor to a list of documents
  documents = list(cursor)
  releaseDbConnection(connection)

  return documents

def getDocumentByDateRange(database_name, collection_name, filters):

  connection = getDbConnection()
  database = connection[str(database_name)]
  collection = database[collection_name]

  cursor = collection.find(filters)

  document = list(cursor)
  releaseDbConnection(connection)

  return documents

## Get Count
def getDocumentCount(database_name, collection_name, filters):
  """Searches for documents in a collection based on a field and value."""
  # Connect to the database
  try:
      connection = getDbConnection()
      database = connection[str(database_name)]
      collection = database[collection_name]

      count = collection.count_documents(filters)

      releaseDbConnection(connection)
      return count
  except Exception as e:
      releaseDbConnection(connection)
      raise e



## Delete the document based on the key value pair. It will remove all the documents which has a matching key
## key value pair. 
def delete_document(database_name, collection_name, delfilter):
  """Deletes a document from a collection based on a field and value and returns deletion information."""
  # Connect to the database
  connection = getDbConnection()
  database = connection[str(database_name)]
  collection = database[collection_name]

  # Create a filter based on the provided search field and value
  #filter = {search_field: search_value}

  # Delete the first matching document (use delete_many for multiple)
  delete_result = collection.delete_many(delfilter)

  # Prepare a dictionary with deletion information
  deletion_info = {
      "deleted_count": delete_result.deleted_count,
      "message": None
  }
  
  releaseDbConnection(connection)
  return delete_result.deleted_count

## Delete the document based on the key value pair. It will remove all the documents which has a matching key
## key value pair.
def delete_document_by_id(database_name, collection_name, document_id):
  """Deletes a document from a collection based on a field and value and returns deletion information."""
  # Connect to the database
  connection = getDbConnection()
  database = connection[str(database_name)]
  collection = database[collection_name]

  # Create a filter based on the provided search field and value
  try:
     _id = connection.common.ObjectId(document_id)
  except(TypeError, ValueError):
     _id = document_id

  filter = {"_id":_id}

  # Delete the first matching document (use delete_many for multiple)
  delete_result = collection.delete_one(filter)
  #print(delete_result)


  # Prepare a dictionary with deletion information
  deletion_info = {
      "deleted_count": delete_result.deleted_count,
      "message": None
  }
  releaseDbConnection(connection)
  return delete_result.deleted_count

#to retrive data from db for RL
def get_all_records(database_name, collection_name):
    try:
        connection = getDbConnection()
        database = connection[str(database_name)]
        collection = database[collection_name]
    except Exception as dbex:
        raise dbex

    try:
        records = list(collection.find({}))
    except Exception as e:
        raise Exception(f"Error in get_all_records: {str(e)}")
    finally:
        releaseDbConnection(connection)
    return records

#update RL data in the db
def update_record(database_name, collection_name, document):
    try:
        connection = getDbConnection()
        database = connection[str(database_name)]
        collection = database[collection_name]
    except Exception as dbex:
            raise dbex

    filter = {"_id": document["_id"]}

    try:
        update_result = collection.update_one(filter, {"$set": document})
        result = update_result.matched_count
    except Exception as e:
        raise Exception(f"Error in update_record: {str(e)}")
    finally:
        releaseDbConnection(connection)

    return result
