import requests
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

username = os.getenv('ATLASSIAN_USERNAME')
password = os.getenv('ATLASSIAN_API_KEY')
domain = os.getenv('DOMAIN')
lead_account_id = os.getenv('LEAD_ACCT_ID')
project_key = os.getenv('PROJECT_KEY')

auth = HTTPBasicAuth(username, password)

# Creates an issue in Jira Cloud using REST API
def create_issue(project_key, issue_type, summary, description):
    try:
        base_url = f'https://{domain}.atlassian.net'
        url = f'{base_url}/rest/api/3/issue'
        headers = {'Content-Type': 'application/json'}
        
        data = {
            'fields': {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type}
            }
        }
        
        response = requests.post(url, json=data, headers=headers, auth=auth)
        response.raise_for_status()  # Raise an error for bad status codes
        # print(response.json().get('key'))
        return response.json().get('key')
    except requests.exceptions.RequestException as error:
        print('error: ')
        print(error.response.json().get('errors'))

# Creates a project for a particular Jira Cloud account and assigns it to a user
def create_project(project_name):
    try:
        base_url = f'https://{domain}.atlassian.net'
        url = f'{base_url}/rest/api/3/project'
        headers = {'Content-Type': 'application/json'}
        
        data = {
            'key': project_key,
            'name': project_name,
            'projectTypeKey': 'software',
            'leadAccountId': lead_account_id
        }
        
        response = requests.post(url, json=data, headers=headers, auth=auth)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # print(response.json())
        return response.json().get('key')
    except requests.exceptions.RequestException as error:
        print('error: ')
        print(error.response.json().get('errors'))

# Deletes an issue by its ID using the Jira Cloud REST API
def delete_issue_by_id(issue_key):
    try:
        base_url = f'https://{domain}.atlassian.net'
        url = f'{base_url}/rest/api/3/issue/{issue_key}'
        headers = {'Content-Type': 'application/json'}
        
        response = requests.delete(url, headers=headers, auth=auth)
        response.raise_for_status() 
        
        # print(response.json())
        return response.json()
    except requests.exceptions.RequestException as error:
        print('error: ')
        print(error.response.json().get('errors'))

# Gets an issue by its ID using the Jira Cloud REST API
def get_issue_by_id(issue_key):
    try:
        base_url = f'https://{domain}.atlassian.net'
        url = f'{base_url}/rest/api/3/issue/{issue_key}'
        headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status() 
        
        # print(response.json())
        return response.json()
    except requests.exceptions.RequestException as error:
        print('error: ')
        print(error.response.json().get('errors'))

# Gets all issues in a particular project using the Jira Cloud REST API
def get_issues():
    try:
        base_url = f'https://{domain}.atlassian.net'
        url = f'{base_url}/rest/api/3/search'
        headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()  # Raise an error for bad status codes
        
        issues = response.json().get('issues', [])
        filtered_issues = [
            {
                'key': issue.get('key'),
                'description': issue.get('fields', {}).get('description'),
                # 'name': issue.get('fields', {}).get('summary'),
                # 'displayName': issue.get('fields', {}).get('assignee', {}).get('displayName')
            }
            for issue in issues
        ]
        
        # print(filtered_issues)
        return filtered_issues
    except requests.exceptions.RequestException as error:
        print('error: ')
        print(error.response.json().get('errors'))

# Gets all projects in a Jira Cloud account using the REST API
def get_projects():
    try:
        base_url = f'https://{domain}.atlassian.net'
        url = f'{base_url}/rest/api/3/project/recent'
        headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()  # Raise an error for bad status codes
        
        projects = response.json()
        filtered_projects = [
            {
                'projectName': project.get('name'),
                'id': project.get('id'),
                'key': project.get('key')
            }
            for project in projects
        ]
        
        # print(filtered_projects)
        return filtered_projects
    except requests.exceptions.RequestException as error:
        print('error: ')
        print(error.response.json().get('errors'))

# List the transitions of a given issue using the Jira Cloud REST API
def get_transitions(issue_key):
    try:
        base_url = f'https://{domain}.atlassian.net'
        url = f'{base_url}/rest/api/3/issue/{issue_key}/transitions'
        headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # print(response.json())
        return response.json()
    except requests.exceptions.RequestException as error:
        print('error: ')
        print(error.response.json().get('errors'))

# Gets all users within a project using Jira Cloud REST API
def get_users():
    try:
        base_url = f'https://{domain}.atlassian.net'
        url = f'{base_url}/rest/api/3/users'
        headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()  # Raise an error for bad status codes
        
        users = response.json()
        filtered_users = [
            {
                'username': user.get('name'),
                'leadAccountId': user.get('accountId'),
                'displayName': user.get('displayName')
            }
            for user in users
        ]
        
        # print(filtered_users)
        return filtered_users
    except requests.exceptions.RequestException as error:
        print('error: ')
        print(error.response.json().get('errors'))

# List the transitions of a given issue using the Jira Cloud REST API
def update_status(issue_key, status_id):
    try:
        base_url = f'https://{domain}.atlassian.net'
        url = f'{base_url}/rest/api/3/issue/{issue_key}/transitions'
        headers = {'Content-Type': 'application/json'}
        
        data = {
            'transition': {
                'id': status_id
            }
        }
        
        response = requests.post(url, json=data, headers=headers, auth=auth)
        response.raise_for_status() 
        
        # If you see that you get status of 204, that means the update worked!
        # print(response.status_code)
        return response.status_code
    except requests.exceptions.RequestException as error:
        print('error: ')
        print(error.response.json().get('errors'))

# If you need to test specific functions, you can uncomment the corresponding lines below
# and provide the necessary arguments.
# if __name__ == "__main__":
#     project_key = 'RDKB'
#     issue_type = 'Bug'
#     summary = 'Issue summary'
#     description = 'Issue description'
#     create_issue(project_key, issue_type, summary, description)
    
#     project_name = 'YOUR_PROJECT_NAME'  # Replace with your actual project name
#     create_project(project_name)
    
#     issue_key = 'RDKB-6'
#     delete_issue_by_id(issue_key)
    
#     issue_key = 'CTTA-2130'
#     get_issue_by_id(issue_key)
    
#     get_issues()
    
#     get_projects()
    
#     issue_key = 'CTTA-2130'
#     get_transitions(issue_key)
    
#     get_users()
    
#     issue_key = 'RDKB-6'
#     status_id = '11'
#     update_status(issue_key, status_id)
