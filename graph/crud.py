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

    def show_relationships(self):
        # Read all persons and their relationships, and return their details as a string
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Person)-[r]->(friend:Person)
                RETURN p.name AS name, p.age AS age, type(r) AS relationship, friend.name AS friend_name
                """
            )
            records = [f"1: {record['name']}, \n {record['relationship']} \n2: {record['friend_name']}" for record in result]
            return "\n\n".join(records) if records else "No persons found."

    
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

    def create_relationship(self, name, friend, relationship):
        with self.driver.session() as session:
            query = f"""
            MATCH (alice:Person {{name: $name}})
            MATCH (bob:Person {{name: $friend}})
            CREATE (alice)-[:{relationship}]->(bob)
            RETURN alice, bob
            """
            result = session.run(query, name=name, friend=friend)
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



    # Filters
    def find_person(self, name):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Person {name: $name})
                OPTIONAL MATCH (p)-[r]->(friend:Person)
                RETURN p.name AS name, p.age AS age, collect({relationship: type(r), friend: friend.name}) AS relationships
                """,
                name=name
            )
            record = result.single()
            if record:
                person_details = f"Name: {record['name']}\nAge: {record['age']}"
                if record['relationships']:
                    relationships = "\n".join(
                        [f"R: {rel['relationship']}, \nFriend: {rel['friend']}\n" for rel in record['relationships']]
                    )
                    person_details += f"\n\nRelationships:\n{relationships}"
                return person_details
            else:
                return f"Person with name '{name}' not found."

    def find_by_relationship(self, relationship_type, friend_name):
        with self.driver.session() as session:
            query = f"""
            MATCH (p:Person)-[r:{relationship_type}]->(friend:Person {{name: $friend_name}})
            RETURN p.name AS name, p.age AS age
            """
            result = session.run(query, friend_name=friend_name)
            records = [f"Name: {record['name']}, Age: {record['age']}" for record in result]
            return "\n".join(records) if records else f"No persons found with relationship '{relationship_type}' to '{friend_name}'."




# Example usage
if __name__ == "__main__":
    db_ops = Neo4jCRUD()

    # Create a person
    # db_ops.create_person("Alice")
    # db_ops.create_person("Bob")
    # db_ops.create_person("Charlie")

    # # Update a person
    # db_ops.update_person("Alice", 42)

    # # Create a relationship
    # db_ops.create_relationship("Alice", "Bob", 's')

    # # Delete a person
    # db_ops.delete_person("Charlie")
    # db_ops.delete_person("Alice")
    # db_ops.delete_person("Bob")

    # print('\n\n\n')




    # db_ops.create_person("DeviceID1")
    # db_ops.create_person("AlarmID1")
    # db_ops.create_person("AlarmID2")
    # db_ops.create_person("AlarmID3")
    # db_ops.create_person("TTID1")
    # db_ops.create_person("TTID2")

    # db_ops.create_relationship("DeviceID1", "AlarmID1", "HAS_ALARM")
    # db_ops.create_relationship("DeviceID1", "AlarmID2", "HAS_ALARM")
    # db_ops.create_relationship("DeviceID1", "AlarmID3", "HAS_ALARM")
    # db_ops.create_relationship("AlarmID1", "TTID1", "HAS_TT")
    # db_ops.create_relationship("AlarmID3", "TTID2", "HAS_TT")
    # db_ops.create_relationship("DeviceID1", "TTID1", "HAS_TT")
    # db_ops.create_relationship("DeviceID1", "TTID2", "HAS_TT")




    # print(db_ops)
    # print(db_ops.show_relationships())
    # print(db_ops.find_person('AlarmID3'))
    # print(db_ops.find_by_relationship("HAS_TT", "TTID1"))

    # Close the connection
    db_ops.close()
