# Mongo-DB

## Routes

- **GET**: `/` : Checks API status.
- **GET**: `/api/jira` : Checks API status.
- **POST**: `/api/jira/create_issue` : Creates an issue.
- **POST**: `/api/jira/create_project` : Creates a project.
- **DELETE**: `/api/jira/delete_issue/<issue_key>` : Deletes an issue by ID.
- **GET**: `/api/jira/get_issue/<issue_key>` : Gets an issue by ID.
- **GET**: `/api/jira/get_issues` : Gets all issues.
- **GET**: `/api/jira/get_projects` : Gets all projects.
- **GET**: `/api/jira/get_transitions/<issue_key>` : Gets transitions for an issue.
- **GET**: `/api/jira/get_users` : Gets all users.
- **POST**: `/api/jira/update_status` : Updates the status of an issue.
