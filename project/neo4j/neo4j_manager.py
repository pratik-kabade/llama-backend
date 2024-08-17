from neo4j import GraphDatabase
from dotenv import load_dotenv
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

# OBJECT is the name of database

class Neo4jManager:
    def __init__(self, username, password, uri, base_uri, llm_model, debug_mode=False):
        # Load environment variables from .env file
        load_dotenv()

        self.username = username
        self.password = password
        self.uri = uri
        self.base_uri = base_uri
        self.llm_model = llm_model
        self.debug_mode = debug_mode

        if self.debug_mode: print('> Initializing Neo4jManager..')

        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
        self.relation_used = 'CONTAINS'
        if self.debug_mode: print('=> Neo4jManager Initialized\n')


    def algo(self, prop, obj_name, value):        
        if self.debug_mode: print('> Creating algo..')
        algo = prop + ' of ' + obj_name + ' is ' + value
        return algo        
        
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
            return "\n".join(objects) if objects else "No objects found.\n"

    def show_relationships(self):
        if self.debug_mode: print('> Showing relationships..')
        # Read all objects and their relationships, and return their details as a string
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:OBJECT)-[r]->(object2:OBJECT)
                RETURN p.name AS name, p.prop AS prop, type(r) AS relationship, object2.name AS object2
                """
            )
            records = [f"1: {record['name']}, \n {record['relationship']} \n2: {record['object2']}" for record in result]
            return "\n\n".join(records) if records else "No objects found.\n"

    def close(self):
        self.driver.close()
        if self.debug_mode: print('=> Driver closed\n')

    def create_object(self, name):
        if self.debug_mode: print('> Creating object..')
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (:OBJECT {name: $name})
                RETURN COUNT(*) AS count
                """,
                name=name
            )
            count = result.single()["count"]
            # print(f"Created {count} node.")
        if self.debug_mode: print('=> Object Created\n')

    def create_property(self, name, prop, value):
        if self.debug_mode:
            print(f'> Creating property->{prop} for {name} as {value}..')
            
        # Construct the Cypher query with dynamic property names
        query = f"""
        MATCH (p:OBJECT {{name: $name}})
        SET p.{prop} = $value
        RETURN p
        """

        with self.driver.session() as session:
            result = session.run(query, name=name, value=value)
            summary = result.consume()
            # print(f"Query counters: {summary.counters}.")
        if self.debug_mode: print(f'=> Property created->{prop} for {name} as {value}\n')

    def create_relationship(self, name, object2, relationship):
        if self.debug_mode: print(f'> Creating relationship {relationship} for {name} with {object2}..')
        with self.driver.session() as session:
            query = f"""
            MATCH (obj1:OBJECT {{name: $name}})
            MATCH (object2:OBJECT {{name: $object2}})
            CREATE (obj1)-[:{relationship}]->(object2)
            RETURN obj1, object2
            """
            result = session.run(query, name=name, object2=object2)
            summary = result.consume()
            # print(f"Query counters: {summary.counters}.")
        if self.debug_mode: print('=> Relationship created {relationship} for {name} with {object2}\n')

    def delete_object(self, name):
        if self.debug_mode: print('> Deleting Object..')
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
            # print(f"Query counters: {summary.counters}.")
        if self.debug_mode: print('=> Object Deleted\n')

    def build_from_csv(self, file, show_progress=False):        
        if self.debug_mode: print('> Building from CSV..')
        lead_object = file.split('/')[-1]
        # print(lead_object)
        self.create_object(lead_object)

        data = pd.read_csv(file)
        header = data.columns.to_numpy()

        progress = len(data)
        for row in range(len(data)):
            first_row_dict = data.iloc[row].to_dict()
            first_element = str(first_row_dict[header[0]])
            self.create_object(first_element)
            self.create_relationship(lead_object, first_element, self.relation_used)

            sentences = ''
            for col in range(len(header)):
                col_name = str(header[col])
                value = str(first_row_dict[header[col]])

                sentence = self.algo(prop=col_name, obj_name=first_element, value=value) 
                # print(sentence)
                sentences += sentence + ', '
                self.create_property(first_element,col_name,value)

            s = str(sentences)
            self.create_property(first_element,'sentences',s)
            if show_progress: print(str(progress) + ' item(s) left..')
            progress -= 1
        if self.debug_mode: print('=> Embeddings Build from CSV completed!\n')
        if self.debug_mode: print()

    def list_all_nodes(self, object_name):
        if self.debug_mode: print('> Listing all nodes..')
        nodes = []
        with self.driver.session() as session:
            query = """
            MATCH (p:OBJECT {name: $object_name})-[r]->(object2:OBJECT)
            RETURN type(r) AS relationship_type, object2.name AS object2
            """
            result = session.run(query, object_name=object_name)
            records = [f"{record['object2']}" for record in result]
            nodes = records

        return nodes if len(nodes)!=0 else f"No relationships found for '{object_name}'."

    def return_prompt_specific_data(self, object_name, prompt, prop='sentences'):
        if self.debug_mode: print('> Returning prompt specific data..')
        item_list = self.list_all_nodes(object_name)
        lowered_item_list = [i.lower() for i in item_list]
        lowered = prompt.lower().split(' ')
        item = ''

        for i in lowered:
            if i in lowered_item_list:
                item = i
        for i in range(len(item_list)):
            if lowered_item_list[i] == item:
                item = item_list[i]

        # all_properties = self.find_by_property(object_name=item, property_type='sentences')

        if item != '':
            if self.debug_mode: print('Item found from the prompt!')
            result = self.find_by_property(object_name=item, property_type=prop)
            return result[0] if len(result)==1 else result
        else:
            print('NO item found from the prompt!')
            return self.return_all_data(object_name=object_name)

    def return_all_data(self, object_name):
        if self.debug_mode: print('> Returning all data..')
        item_list = self.list_all_nodes(object_name)

        all_properties = []
        for item in item_list:
            all_properties.append(self.find_by_property(object_name=item, property_type='sentences'))

        return all_properties

    def query_data_by_key(self, primary_object, primary_key, secondary_property):
        if self.debug_mode: print(f'> Querying {secondary_property},[obj2] (=>) on {primary_object},[OBJ1]..')
        primary_key_value = self.find_by_property(primary_object, primary_key)
        if self.debug_mode: print(f'-----> Value of {primary_key} is {primary_key_value}')
        secondary_property_value = []
        if type(primary_key_value) == list:
            for i in primary_key_value:
                secondary_property_value.append(self.find_by_property(i, secondary_property))
        else:
            secondary_property_value.append(self.find_by_property(primary_key_value, secondary_property))
        if self.debug_mode: print(f'-----> {secondary_property} of {primary_object} is {secondary_property_value}')
        return secondary_property_value

    def merge_properties(self, FILE1, file2, primary_key, show_progress=False):
        if self.debug_mode: print(f'> Merging {file2},[file2] (=>) on {FILE1},[FILE1]..')
        FILE1_nodes = self.list_all_nodes(FILE1)
        file2_nodes = self.list_all_nodes(file2)
        progress = len(FILE1_nodes)
        for FILE1_node in FILE1_nodes:
            FILE1_ids = self.find_by_property(FILE1_node, primary_key)
            
            for file1_id in FILE1_ids:
                ID = str(file1_id)
                index = -1

                # Find ID from file2_nodes
                for idx, node in enumerate(file2_nodes):
                    properties = self.find_all_properties(node)
                    found = False
                    for key, value in properties.items():
                        if key == primary_key and value == ID:
                            index = idx
                            found = True
                            break
                    if found:
                        break
                            
                # Avoid creating duplicate keys
                dict = self.find_all_properties(FILE1_node)
                old_items = []
                for k,v in dict.items():
                    old_items.append(k)
                    
                # Indexing
                item_to_change = file2_nodes[index]
                dict = self.find_all_properties(item_to_change)
                if index != -1:                
                    for k,v in dict.items():                    
                        if k not in old_items:
                            self.create_property(FILE1_node,k,v)
                else:
                    print(f"No matching '{primary_key}' found for '{ID}' in '{file2}'")
            if show_progress: print(str(progress) + ' item(s) left..')
            progress -= 1

        if self.debug_mode: print(f'=> Merged {file2},[file2] (=>) on {FILE1},[FILE1]\n')



    # DB_Ops
    def db_op_create_database(self, database_name): #BUG
        if self.debug_mode: print('> DB-Operation: Creating Database..')
        url = f"{self.base_uri}/db/system/tx/commit"
        headers = {
            "Content-Type": "application/json"
        }
        query = {
            "statements": [
                {
                    "statement": f"CREATE DATABASE {database_name}",
                    "resultDataContents": []
                }
            ]
        }
        response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code == 200:
            print(f"Database '{database_name}' created successfully.")
        else:
            print("Failed to create database:", response.status_code, response.text)

    def db_op_get_databases(self):
        if self.debug_mode: print('> DB-Operation: getting all databases..')
        url = f"{self.base_uri}/db/system/tx/commit"
        headers = {
            "Content-Type": "application/json"
        }
        query = {
            "statements": [
                {
                    "statement": "SHOW DATABASES",
                    "resultDataContents": ["row"]
                }
            ]
        }
        response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code == 200:
            result = response.json()
            # print("Raw response:", result)
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
            else:
                print("No databases found or query did not return results.")
        else:
            print("Failed to retrieve databases:", response.status_code, response.text)

    def db_op_get_database_data(self, database_name):
        if self.debug_mode: print('> DB-Operation: getting database data..')
        url = f"{self.base_uri}/db/{database_name}/tx/commit"
        headers = {
            "Content-Type": "application/json"
        }
        query = {
            "statements": [
                {
                    "statement": "MATCH (n) RETURN n LIMIT 25",
                    "resultDataContents": ["row", "graph"]
                }
            ]
        }
        response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code == 200:
            result = response.json()
            # print("Raw response:", result)
            if 'results' in result and result['results']:
                for record in result['results'][0]['data']:
                    # Safely access node details
                    row = record['row']
                    print(f"Node: {row}")
                    print("-" * 40)
            else:
                print("No data found or query did not return results.")
        else:
            print("Failed to retrieve data:", response.status_code, response.text)

    def delete_all_data(self, database_name):
        if self.debug_mode: print('> DB-Operation: deleting database..')
        url = f"{self.base_uri}/db/{database_name}/tx/commit"
        headers = {
            "Content-Type": "application/json"
        }
        query = {
            "statements": [
                {
                    "statement": "MATCH (n) DETACH DELETE n",
                    "resultDataContents": []
                }
            ]
        }
        response = requests.post(url, json=query, headers=headers, auth=HTTPBasicAuth(self.username, self.password))
        if response.status_code == 200:
            print(f"All data from '{database_name}' deleted successfully.")
        else:
            print("Failed to delete data:", response.status_code, response.text)



    # Filters
    def find_object(self, name):
        if self.debug_mode: print('> Filters: finding object..')
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
        if self.debug_mode: print('> Filters: finding relationship..')
        with self.driver.session() as session:
            query = f"""
            MATCH (p:OBJECT)-[r:{relationship_type}]->(object2:OBJECT {{name: $object2}})
            RETURN p.name AS name, p.prop AS prop
            """
            result = session.run(query, object2=object2)
            records = [f"Name: {record['name']}" for record in result]
            return "\n".join(records) if records else f"No objects found with relationship '{relationship_type}' to '{object2}'."

    def find_by_property(self, object_name, property_type):
        if self.debug_mode: print('> Filters: finding property..')
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
        if self.debug_mode: print('> Filters: finding all relationship..')
        with self.driver.session() as session:
            query = """
            MATCH (p:OBJECT {name: $object_name})-[r]->(object2:OBJECT)
            RETURN type(r) AS relationship_type, object2.name AS object2
            """
            result = session.run(query, object_name=object_name)
            records = [f"Relationship: {record['relationship_type']}, Object2: {record['object2']}" for record in result]
            return "\n".join(records) if records else f"No relationships found for '{object_name}'."

    def find_all_properties(self, object_name):
        if self.debug_mode: print('> Filters: finding all properties..')
        with self.driver.session() as session:
            query = """
            MATCH (p:OBJECT {name: $object_name})
            RETURN p
            """
            result = session.run(query, object_name=object_name)
            
            # Extract the properties from the node
            properties = {}
            for record in result:
                node = record["p"]
                properties = dict(node)  # Convert the node's properties to a dictionary
            
            return properties if properties else f"No properties found for '{object_name}'."


# Example usage
if __name__ == "__main__":
    username = 'neo4j'
    password = '123'
    uri = 'bolt://localhost:7687'
    base_uri = 'http://localhost:7474'
    llm_model = 'llama2'

    db = Neo4jManager(username, password, uri, base_uri, llm_model, True)

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

    # print(db)
    # print(db.show_relationships())
    # print(db.find_object('DeviceID1'))
    # print(db.find_by_relationship("TTID2", "HAS_TT2"))

    # # db.build_from_csv('./data/Alarms.csv')
    # db.build_from_csv('./data/f1.csv')
    # db.build_from_csv('./data/f2.csv')
    # print(db.query_data_by_key(primary_object='4115', primary_key='RESID', secondary_property='desc', 
    #                           _file1='f1.csv', _file2='f2.csv'))
    # print(db.find_by_property('RES1', 'RESID'))
    # print(db)
    # db.build_from_csv('./data/Alarms.csv')
    # print(db.find_all_properties('HETN'))
    # print(db.find_all_relationships('HETN'))
    # print(db.list_all_nodes('Alarms.csv'))
    # print(db.find_by_property('ADIQ', 'Northings'))
    # print(db.find_by_property('HETN', 'FirstOccurrence'))

    # prompt = 'what is NANP ?'

    # print(db.return_prompt_specific_data('Alarms.csv',prompt))
    # db.return_all_data('Alarms.csv')

    db.delete_all_data('neo4j')
    file1 = 'employees.csv'
    file2 = 'compensation.csv'
    file3 = 'work_experience.csv'
    pk = 'id'
    db.build_from_csv('data/sample/compensation.csv')
    db.build_from_csv('data/sample/employees.csv')
    db.build_from_csv('data/sample/work_experience.csv')
    db.merge_properties(file1, file2, pk)
    db.merge_properties(file1, file3, pk, True)
    print(db.find_by_property('Charlie', 'experience'))

    # db.delete_all_data('neo4j')
    # Close the connection
    db.close()
