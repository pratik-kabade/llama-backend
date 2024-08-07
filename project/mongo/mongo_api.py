import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from mongo_settings import (
    create_document,
    get_document_by_id,
    delete_document_by_id,
    get_all_documents,
    update_document_by_id
)

# Load environment variables
load_dotenv()

# MongoDB configuration
PORT = os.getenv('MONGO_PORT', 4001)

# Flask app setup
app = Flask(__name__)

# Flask routes
@app.route('/', methods=['GET'])
def api_check():
    res = {'response':200}
    return jsonify(res)

@app.route('/api/mongo', methods=['GET'])
def api_check():
    res = {'response':200}
    return jsonify(res)

@app.route('/api/mongo/create_document', methods=['POST'])
def api_create_document():
    data = request.json
    collection_name = data['collection_name']
    document = data['document']
    result = create_document(collection_name, document)
    return jsonify({'result': result})

@app.route('/api/mongo/get_document/<collection_name>/<doc_id>', methods=['GET'])
def api_get_document(collection_name, doc_id):
    result = get_document_by_id(collection_name, doc_id)
    return jsonify(result)

@app.route('/api/mongo/delete_document/<collection_name>/<doc_id>', methods=['DELETE'])
def api_delete_document(collection_name, doc_id):
    result = delete_document_by_id(collection_name, doc_id)
    return jsonify({'deleted_count': result})

@app.route('/api/mongo/get_all_documents/<collection_name>', methods=['GET'])
def api_get_all_documents(collection_name):
    result = get_all_documents(collection_name)
    return jsonify(result)

@app.route('/api/mongo/update_document', methods=['POST'])
def api_update_document():
    data = request.json
    collection_name = data['collection_name']
    doc_id = data['doc_id']
    update_fields = data['update_fields']
    result = update_document_by_id(collection_name, doc_id, update_fields)
    return jsonify({'modified_count': result})

if __name__ == '__main__':
    app.run(port=PORT, debug=True)
    
