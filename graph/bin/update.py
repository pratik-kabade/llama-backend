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
        # Execute a query to update a person's age
        result = session.run(
            """
            MATCH (p:Person {name: $name})
            SET p.age = $age
            RETURN p
            """,
            name="Alice",
            age=42
        )
        
        records = result.data()
        summary = result.consume()
        
        # Print query counters
        print(f"Query counters: {summary.counters}.")
