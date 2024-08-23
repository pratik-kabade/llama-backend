import requests
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import json

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

# Gets comments of an issue by its ID using the Jira Cloud REST API
def get_comments_by_id(issue_key):
    try:
        base_url = f'https://{domain}.atlassian.net'
        url = f'{base_url}/rest/api/3/issue/{issue_key}'
        headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status() 
        
        issue_details = response.json()
        comments = issue_details.get('fields', {}).get('comment', {}).get('comments', [])
        
        filtered_details = [
            comment.get('body', {}).get('content', [])[0].get('content', [])[0].get('text', '')
            for comment in comments
        ]
        return filtered_details
    except requests.exceptions.RequestException as error:
        print('error: ')
        print(error.response.json().get('errors'))

# Gets all issues in a particular project using the Jira Cloud REST API
def get_issues(results=10, get_all=False):
    try:
        base_url = f'https://{domain}.atlassian.net'
        url = f'{base_url}/rest/api/3/search'
        headers = {'Content-Type': 'application/json'}
        start_at = 0
        all_issues = []  # This will accumulate all issues
        
        while True:
            params = {
                'maxResults': results,
                'startAt': start_at
            }
            
            response = requests.get(url, headers=headers, auth=auth, params=params)
            response.raise_for_status()
            
            issues = response.json().get('issues', [])
            all_issues.extend(issues)  # Extend the list with the new issues

            if len(issues) <= params['maxResults']:
                break  # No more issues to fetch
            start_at += params['maxResults']
        
        filtered_issues = [
            # TODO comments, parent
            {
                'key': issue.get('key'),
                'summary': issue.get('fields', {}).get('summary'),
                'description': issue.get('fields', {}).get('description').get('content')[0].get('content')[0].get('text'),
                'status': issue.get('fields', {}).get('status').get('name'),
                'labels': issue.get('fields', {}).get('labels'),
                'comments': get_comments_by_id(issue.get('key')),
                'issuelinks': (
                    issue.get('fields', {}).get('issuelinks', [])
                    [0].get('inwardIssue', {}).get('key', '')
                    if issue.get('fields', {}).get('issuelinks') and len(issue.get('fields', {}).get('issuelinks', [])) > 0
                    else None
                ),

                # 'displayName': issue.get('fields', {}).get('assignee', {}).get('displayName')
            }
            for issue in all_issues  # Process all accumulated issues
        ]
        
        # print(filtered_issues)
        return all_issues if get_all else filtered_issues
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

if __name__ == "__main__":
    issues = get_issues()
    json_string = json.dumps(issues)

    json_value = json.loads(json_string)
    with open('issues_all.json', 'w') as file:
        json.dump(json_value, file, indent=4)
    print('done!')

