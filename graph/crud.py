from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

class Neo4jCRUD:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        self.username = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.uri = os.getenv("NEO4J_URI")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
        
    def __str__(self):
        # Read all persons and return their details as a string
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Person)
                RETURN p.name AS name, p.age AS age
                """
            )
            persons = [f"Name: {record['name']}, Age: {record['age']}" for record in result]
            return "\n".join(persons) if persons else "No persons found."

    
    def close(self):
        self.driver.close()

    def create_person(self, name):
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (:Person {name: $name})
                RETURN COUNT(*) AS count
                """,
                name=name
            )
            count = result.single()["count"]
            print(f"Created {count} nodes.")

    def update_person(self, name, age):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Person {name: $name})
                SET p.age = $age
                RETURN p
                """,
                name=name,
                age=age
            )
            summary = result.consume()
            print(f"Query counters: {summary.counters}.")

    def create_relationship(self, name, friend):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (alice:Person {name: $name})
                MATCH (bob:Person {name: $friend})
                CREATE (alice)-[:KNOWS]->(bob)
                RETURN alice, bob
                """,
                name=name,
                friend=friend
            )
            summary = result.consume()
            print(f"Query counters: {summary.counters}.")

    def delete_person(self, name):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Person {name: $name})
                DETACH DELETE p
                RETURN p
                """,
                name=name
            )
            summary = result.consume()
            print(f"Query counters: {summary.counters}.")

# Example usage
if __name__ == "__main__":
    neo4j_crud = Neo4jCRUD()

    # Create a person
    neo4j_crud.create_person("Alice")
    neo4j_crud.create_person("Bob")
    neo4j_crud.create_person("Charlie")

    # Update a person
    neo4j_crud.update_person("Alice", 42)

    # Create a relationship
    neo4j_crud.create_relationship("Alice", "Bob")

    # Delete a person
    neo4j_crud.delete_person("Charlie")

    print('\n\n\n')
    print(neo4j_crud)

    # Close the connection
    neo4j_crud.close()
