import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables from .env file
load_dotenv()

username = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")
base_uri =  os.getenv("NEO4J_BASEURL")


url = f"{base_uri}/db/neo4j/tx/commit"

headers = {
    "Content-Type": "application/json"
}

query = {
    "statements": [
        {
            "statement": "RETURN 1 AS number",
            "resultDataContents": ["row"]
        }
    ]
}

response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(username, password))


if response.status_code == 200:
    result = response.json()
    # Print the raw result to debug the response structure
    print("Raw response:", result)
    
    # Check if results are returned and print the databases
    if 'results' in result and result['results']:
        for record in result['results'][0]['data']:
            # Safely access database details
            row = record['row']
            db_name = row[0] if len(row) > 0 else "N/A"
            db_status = row[1] if len(row) > 1 else "N/A"
            db_size = row[2] if len(row) > 2 else "N/A"  # Size may not be available in all cases
            
            print(f"\nDatabase Name: {db_name}")
            print(f"Status: {db_status}")
            print(f"Size: {db_size}")
            print("-" * 40)
    else:
        print("No databases found or query did not return results.")
else:
    print("Failed to retrieve databases:", response.status_code, response.text)