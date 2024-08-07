from pymongo import MongoClient
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')
PORT = os.getenv('MONGO_PORT', 4001)

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Create a new document in a specified collection
def create_document(collection_name, document):
    try:
        collection = db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except Exception as e:
        print(f'Error: {e}')
        return None

# Get a document by its ID
def get_document_by_id(collection_name, doc_id):
    try:
        collection = db[collection_name]
        document = collection.find_one({"_id": doc_id})
        return document
    except Exception as e:
        print(f'Error: {e}')
        return None

# Delete a document by its ID
def delete_document_by_id(collection_name, doc_id):
    try:
        collection = db[collection_name]
        result = collection.delete_one({"_id": doc_id})
        return result.deleted_count
    except Exception as e:
        print(f'Error: {e}')
        return None

# Get all documents from a collection
def get_all_documents(collection_name):
    try:
        collection = db[collection_name]
        documents = list(collection.find())
        return documents
    except Exception as e:
        print(f'Error: {e}')
        return None

# Update a document by its ID
def update_document_by_id(collection_name, doc_id, update_fields):
    try:
        collection = db[collection_name]
        result = collection.update_one({"_id": doc_id}, {"$set": update_fields})
        return result.modified_count
    except Exception as e:
        print(f'Error: {e}')
        return None

if __name__ == '__main__':
    collection_name = 'your_collection_name'
    document = {
        'key1': 'value1',
        'key2': 'value2'
    }
    create_document(collection_name, document)

    print(get_all_documents('your_collection_name'))

    collection_name = 'your_collection_name'
    doc_id = 'your_document_id'
    print(get_document_by_id(collection_name, doc_id))

