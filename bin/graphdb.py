from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

class Neo4jGraphDB:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_relationship(self, start_node_element_id, end_node_element_id, relationship_type, **properties):
        query = """
        MATCH (a), (b)
        WHERE id(a) = $start_node_element_id AND id(b) = $end_node_element_id
        CREATE (a)-[r:KNOWS { since: $since }]->(b)
        RETURN r
        """
        
        params = {
            "start_node_element_id": start_node_element_id,
            "end_node_element_id": end_node_element_id,
            "since": properties.get("since", None)
        }
        
        print(f"Running query: {query}")
        print(f"With parameters: {params}")
        
        try:
            with self._driver.session() as session:
                result = session.run(query, **params)
                single_result = result.single()
                if single_result:
                    return single_result[0]
                else:
                    print("No result returned from relationship creation query.")
                    return None
        except Exception as e:
            print(f"Error occurred while creating relationship: {e}")
            return None

    def create_node(self, label, properties):
        properties_str = ', '.join([f"{key}: '{value}'" for key, value in properties.items()])
        query = f"CREATE (n:{label} {{{properties_str}}}) RETURN id(n)"
        
        try:
            with self._driver.session() as session:
                result = session.run(query)
                node_id = result.single()
                if node_id:
                    return node_id[0]
                else:
                    print("No result returned from node creation query.")
                    return None
        except Exception as e:
            print(f"Error occurred while creating node: {e}")
            return None

    def get_node_by_id(self, element_id):
        query = "MATCH (n) WHERE id(n) = $element_id RETURN n"
        try:
            with self._driver.session() as session:
                result = session.run(query, element_id=element_id)
                node = result.single()
                if node:
                    return node[0]
                else:
                    print("No node found with the specified ID.")
                    return None
        except Exception as e:
            print(f"Error occurred while retrieving node: {e}")
            return None


# Initialize Neo4j database connection
db = Neo4jGraphDB(uri, user, password)

# Create or retrieve nodes
node1 = db.create_node("Person", {"name": "Alice"})
node2 = db.create_node("Person", {"name": "Bob"})

if node1 and node2:
    print(f"Node1 ID: {node1}")
    print(f"Node2 ID: {node2}")
    relationship = db.create_relationship(node1, node2, "KNOWS", since=2024)
    if relationship:
        print("Relationship created:", relationship)
    else:
        print("Failed to create relationship")
else:
    print("One or both nodes were not created or retrieved")

db.close()
