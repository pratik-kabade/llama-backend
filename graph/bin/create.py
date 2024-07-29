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
    driver.verify_connectivity()

    with driver.session() as session:
        result = session.run(
            "CREATE (:Person {name: $name}) RETURN COUNT(*) AS count",
            name="Alice"
        )
        count = result.single()["count"]
        print(f"Created {count} nodes.")
