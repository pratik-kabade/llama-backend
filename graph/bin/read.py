from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

username = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")
uri = os.getenv("NEO4J_URI")

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = uri
AUTH = (username, password)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    with driver.session() as session:
        # Query to match Person nodes
        result = session.run(
            "MATCH (p:Person) RETURN p.name AS name"
        )
        
        records = result.data()
        summary = result.consume()
        
        # Loop through results and do something with them
        for record in records:
            print(record)  # Obtain record as dict

        # Summary information
        print("The query returned {records_count} records in {time} ms.".format(
            records_count=len(records),
            time=summary.result_available_after
        ))
