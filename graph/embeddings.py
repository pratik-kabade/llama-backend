from neo4j import GraphDatabase
import requests
import pandas as pd
from io import StringIO
import os
from dotenv import load_dotenv
import json

'''
Loads CSV data into Neo4j: 
    Fetches a CSV file from a URL, processes it, and 
    creates nodes and relationships in the Neo4j database.
Retrieves answers from Neo4j: 
    Provides a method to query the database for answers to specific questions.
'''

class Neo4jClient:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.uri = os.getenv('NEO4J_URI')
        self.user = os.getenv('NEO4J_USER')
        self.password = os.getenv('NEO4J_PASSWORD')
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def load_csv_to_neo4j(self, csv_url):
        # Fetch the CSV file
        response = requests.get(csv_url)
        response.raise_for_status()  # Ensure the request was successful

        # Read the CSV data into a DataFrame
        df = pd.read_csv(StringIO(response.text))

        # Prepare a dictionary to store embeddings
        embeddings = {
            "questions": [],
            "answers": []
        }

        # Create nodes and relationships
        with self.driver.session() as session:
            for _, row in df.iterrows():
                question_text = row['question']
                question_embedding = row['question_embedding']
                answer_text = row['answer']
                answer_embedding = row['answer_embedding']

                # Add embeddings to the dictionary
                embeddings["questions"].append({
                    "text": question_text,
                    "embedding": question_embedding
                })
                embeddings["answers"].append({
                    "text": answer_text,
                    "embedding": answer_embedding
                })

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
        
        # # Save embeddings to a JSON file
        # with open('./graph/embeddings.json', 'w') as json_file:
        #     json.dump(embeddings, json_file, indent=4)
        # print(Saved embeddings to 'embeddings.json')
        
        print('Loaded CSV into Neo4j')

    def get_answer(self, question_text):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (q:Question {text: $question_text})-[:ANSWERED_BY]->(a:Answer)
                RETURN a.text AS answer
                """,
                question_text=question_text
            )
            answers = [record["answer"] for record in result]
        return answers

    def print_all_data(self):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (q:Question)-[:ANSWERED_BY]->(a:Answer)
                RETURN q.text AS question, a.text AS answer
                """
            )
            for record in result:
                print(f"Question: {record['question']}\nAnswer: {record['answer']}\n")



if __name__ == "__main__":
    # URL of the CSV file
    csv_url = 'https://data.neo4j.com/llm-vectors-unstructured/Quora-QuAD-1000-embeddings.csv'
    
    # Initialize Neo4j client and load data
    client = Neo4jClient()
    # client.load_csv_to_neo4j(csv_url)

    # # Example usage
    # client.print_all_data()
    question = 'What song has the lyrics "someone left the cake out in the rain"?'
    answers = client.get_answer(question)
    print(f"Question: \n{question}\n\nAnswers:")
    for answer in answers:
        print(answer)
