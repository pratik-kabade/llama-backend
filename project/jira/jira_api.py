from flask import Flask, request, jsonify
from jira_settings import JiraSetting
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PORT = os.getenv('JIRA_PORT', 4000)

app = Flask(__name__)
jira = JiraSetting()

@app.route('/', methods=['GET'])
def api_check():
    res = {'response':200}
    return jsonify(res)

@app.route('/api/jira', methods=['GET'])
def jira_api_check():
    res = {'response':200}
    return jsonify(res)

@app.route('/api/jira/create_issue', methods=['POST'])
def api_create_issue():
    data = request.json
    result = jira.create_issue(data['project_key'], data['issue_type'], data['summary'], data['description'])
    return jsonify(result)

@app.route('/api/jira/create_project', methods=['POST'])
def api_create_project():
    data = request.json
    result = jira.create_project(data['project_name'])
    return jsonify(result)

@app.route('/api/jira/delete_issue/<issue_key>', methods=['DELETE'])
def api_delete_issue(issue_key):
    result = jira.delete_issue_by_id(issue_key)
    return jsonify(result)

@app.route('/api/jira/get_issue/<issue_key>', methods=['GET'])
def api_get_issue(issue_key):
    result = jira.get_issue_by_id(issue_key)
    return jsonify(result)

@app.route('/api/jira/get_issues/<num>', methods=['GET'])
def api_get_issues(num):
    num=int(num)
    result = jira.get_issues(num)
    return jsonify(result)

@app.route('/api/jira/get_projects', methods=['GET'])
def api_get_projects():
    result = jira.get_projects()
    return jsonify(result)

@app.route('/api/jira/get_transitions/<issue_key>', methods=['GET'])
def api_get_transitions(issue_key):
    result = jira.get_transitions(issue_key)
    return jsonify(result)

@app.route('/api/jira/get_users', methods=['GET'])
def api_get_users():
    result = jira.get_users()
    return jsonify(result)

@app.route('/api/jira/update_status', methods=['POST'])
def api_update_status():
    data = request.json
    result = jira.update_status(data['issue_key'], data['status_id'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=PORT, debug=True)
