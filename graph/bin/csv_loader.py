# neo4j csv loader

from neo4j import GraphDatabase
import requests
import pandas as pd
from io import StringIO

# Neo4j connection details
uri = "bolt://localhost:7687"  # Update this with your Neo4j URI
user = "neo4j"  # Update with your Neo4j username
password = "123"  # Update with your Neo4j password

# Initialize Neo4j driver
driver = GraphDatabase.driver(uri, auth=(user, password))

def load_csv_to_neo4j(csv_url):
    # Fetch the CSV file
    response = requests.get(csv_url)
    response.raise_for_status()  # Ensure the request was successful

    # Read the CSV data into a DataFrame
    df = pd.read_csv(StringIO(response.text))

    # Create nodes and relationships
    with driver.session() as session:
        for _, row in df.iterrows():
            question_text = row['question']
            question_embedding = row['question_embedding']
            answer_text = row['answer']
            answer_embedding = row['answer_embedding']

            # Merge Question node
            session.execute_write(lambda tx: tx.run(
                """
                MERGE (q:Question {text: $text})
                SET q.embedding = $embedding
                RETURN q
                """, text=question_text, embedding=question_embedding))

            # Merge Answer node
            session.execute_write(lambda tx: tx.run(
                """
                MERGE (a:Answer {text: $text})
                SET a.embedding = $embedding
                RETURN a
                """, text=answer_text, embedding=answer_embedding))

            # Create relationship
            session.execute_write(lambda tx: tx.run(
                """
                MATCH (q:Question {text: $question_text})
                MATCH (a:Answer {text: $answer_text})
                MERGE (q)-[:ANSWERED_BY]->(a)
                """, question_text=question_text, answer_text=answer_text))

# URL of the CSV file
csv_url = 'https://data.neo4j.com/llm-vectors-unstructured/Quora-QuAD-1000-embeddings.csv'

# Load data into Neo4j
load_csv_to_neo4j(csv_url)
