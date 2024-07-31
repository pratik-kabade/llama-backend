from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import pandas as pd

# OBJECT is the name of database

class Neo4jCRUD:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        self.username = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.uri = os.getenv("NEO4J_URI")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
        
    def __str__(self):
        # Read all objects and return their details as a string
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT)
                RETURN p.name AS name, p.prop AS prop
                """
            )
            objects = [f"Name: {record['name']}" for record in result]
            return "\n".join(objects) if objects else "No objects found."

    def show_relationships(self):
        # Read all objects and their relationships, and return their details as a string
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT)-[r]->(object2:OBJECT)
                RETURN p.name AS name, p.prop AS prop, type(r) AS relationship, object2.name AS object2
                """
            )
            records = [f"1: {record['name']}, \n {record['relationship']} \n2: {record['object2']}" for record in result]
            return "\n\n".join(records) if records else "No objects found."

    def close(self):
        self.driver.close()

    def create_object(self, name):
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (:OBJECT {name: $name})
                RETURN COUNT(*) AS count
                """,
                name=name
            )
            count = result.single()["count"]
            print(f"Created {count} node.")

    def update_object(self, name, prop):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT {name: $name})
                SET p.prop = $prop
                RETURN p
                """,
                name=name,
                prop=prop
            )
            summary = result.consume()
            print(f"Query counters: {summary.counters}.")

    def create_relationship(self, name, object2, relationship):
        with self.driver.session() as session:
            query = f"""
            MATCH (obj1:OBJECT {{name: $name}})
            MATCH (object2:OBJECT {{name: $object2}})
            CREATE (obj1)-[:{relationship}]->(object2)
            RETURN obj1, object2
            """
            result = session.run(query, name=name, object2=object2)
            summary = result.consume()
            print(f"Query counters: {summary.counters}.")

    def delete_object(self, name):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT {name: $name})
                DETACH DELETE p
                RETURN p
                """,
                name=name
            )
            summary = result.consume()
            print(f"Query counters: {summary.counters}.")


    def build_from_csv(self, file):
        data = pd.read_csv(file)
        header = data.columns.to_numpy()
        for row in range(len(data)):
            first_row_dict = data.iloc[row].to_dict()
            first_element = first_row_dict[header[0]]
            self.create_object(first_element)

            for col in range(len(header)):
                col_name = header[col]
                value = first_row_dict[header[col]]
                # print(first_row_dict[header[0]] ,'|||', col_name ,'|||', value)

                with self.driver.session() as session:
                    query = f"""
                    MATCH (p:OBJECT {{name: $name}})
                    SET p.{col_name} = $value
                    RETURN p
                    """
                    result = session.run(query, name=first_row_dict[header[0]], value=value)
                    summary = result.consume()

                    # print(f"Query counters: {summary.counters}.")




    # Filters
    def find_object(self, name):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT {name: $name})
                OPTIONAL MATCH (p)-[r]->(object2:OBJECT)
                RETURN p.name AS name, p.prop AS prop, collect({relationship: type(r), object2: object2.name}) AS relationships
                """,
                name=name
            )
            record = result.single()
            if record:
                object_details = f"Name: {record['name']}\nProperty: {record['prop']}"
                if record['relationships']:
                    relationships = "\n".join(
                        [f"R: {rel['relationship']}, \nObject2: {rel['object2']}\n" for rel in record['relationships']]
                    )
                    object_details += f"\n\nRelationships:\n{relationships}"
                return object_details
            else:
                return f"OBJECT with name '{name}' not found."

    def find_by_relationship(self, object2, relationship_type):

        with self.driver.session() as session:
            query = f"""
            MATCH (p:OBJECT)-[r:{relationship_type}]->(object2:OBJECT {{name: $object2}})
            RETURN p.name AS name, p.prop AS prop
            """
            result = session.run(query, object2=object2)
            records = [f"Name: {record['name']}" for record in result]
            return "\n".join(records) if records else f"No objects found with relationship '{relationship_type}' to '{object2}'."

    def find_by_property(self, object_name, property_type):
        with self.driver.session() as session:
            query = """
            MATCH (p:OBJECT {name: $object_name})
            RETURN p
            """
            result = session.run(query, object_name=object_name)
            records = [record["p"] for record in result]
            if not records:
                return f"No properties found for '{object_name}'."
            
            property_values = [record[property_type] for record in records if property_type in record]
            if not property_values:
                return f"No properties of type '{property_type}' found for '{object_name}'."
            
            return property_values


    def find_all_relationships(self, object_name):
        with self.driver.session() as session:
            query = """
            MATCH (p:OBJECT {name: $object_name})-[r]->(object2:OBJECT)
            RETURN type(r) AS relationship_type, object2.name AS object2
            """
            result = session.run(query, object_name=object_name)
            records = [f"Relationship: {record['relationship_type']}, Object2: {record['object2']}" for record in result]
            return "\n".join(records) if records else f"No relationships found for '{object_name}'."

    def find_all_properties(self, object_name):
        with self.driver.session() as session:
            query = """
            MATCH (p:OBJECT {name: $object_name})
            RETURN p
            """
            result = session.run(query, object_name=object_name)
            records = [record["p"] for record in result]
            return records if records else f"No properties found for '{object_name}'."


# Example usage
if __name__ == "__main__":
    db = Neo4jCRUD()

    # Create
    # db.create_object("Alice")
    # db.create_object("Bob")
    # db.create_object("Charlie")

    # # Update
    # db.update_object("Alice", 42)

    # # Create a relationship
    # db.create_relationship("Alice", "Bob", 's')

    # # Delete
    # db.delete_object("Charlie")
    # db.delete_object("Alice")
    # db.delete_object("Bob")

    # print('\n\n\n')




    # db.create_object("DeviceID1")
    # db.create_object("AlarmID1")
    # db.create_object("AlarmID2")
    # db.create_object("AlarmID3")
    # db.create_object("TTID1")
    # db.create_object("TTID2")

    # db.create_relationship("DeviceID1", "AlarmID1", "HAS_ALARM")
    # db.create_relationship("DeviceID1", "AlarmID2", "HAS_ALARM")
    # db.create_relationship("DeviceID1", "AlarmID3", "HAS_ALARM")
    # db.create_relationship("AlarmID1", "TTID1", "HAS_TT")
    # db.create_relationship("AlarmID3", "TTID2", "HAS_TT")
    # db.create_relationship("DeviceID1", "TTID1", "HAS_TT")
    # db.create_relationship("DeviceID1", "TTID2", "HAS_TT")
    # db.create_relationship("DeviceID1", "TTID2", "HAS_TT2")



    # db.update_object("AlarmID3", 'Closed')

    print(db)
    # print(db.show_relationships())
    # print(db.find_object('DeviceID1'))
    # print(db.find_by_relationship("TTID2", "HAS_TT2"))

    # db.create_object("NANP")
    # db.build_from_csv('./data/Alarms.csv')
    # print(db.find_all_properties('HETN'))
    # print(db.find_by_property('ADIQ', 'Northings'))
    # print(db.find_by_property('HETN', 'FirstOccurrence'))

    # Close the connection
    db.close()