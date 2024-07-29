# neo4j retriever

from neo4j import GraphDatabase

# Neo4j connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "123"

# Initialize Neo4j driver
driver = GraphDatabase.driver(uri, auth=(user, password))

def get_answer(question_text):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (q:Question {text: $question_text})-[:ANSWERED_BY]->(a:Answer)
            RETURN a.text AS answer
            """,
            question_text=question_text
        )
        answers = [record["answer"] for record in result]
    return answers

# Example usage
question = 'What song has the lyrics "someone left the cake out in the rain"?'
answers = get_answer(question)
print(f"Question: '{question}':\n\n")
for answer in answers:
    print(answer)
