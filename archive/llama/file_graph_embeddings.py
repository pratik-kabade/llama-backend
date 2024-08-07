# import os
# import numpy as np
# from neo4j import GraphDatabase
# from sentence_transformers import SentenceTransformer
# import json
# import requests
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Neo4j connection settings
# uri = "bolt://localhost:7687"
# username = "neo4j"
# password = os.getenv("NEO4J_PASSWORD")

# # Ollama API URL
# OLLAMA_API_URL = os.getenv("LLM_GENERATE_URL")

# class VectorEmbeddingManager:
#     def __init__(self, neo4j_uri, neo4j_user, neo4j_password, db_name):
#         self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
#         self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
#         self.db_name = db_name

#     def extract_text_from_pdf(self, pdf_path):
#         from PyPDF2 import PdfReader
#         reader = PdfReader(pdf_path)
#         text = ''
#         for page in reader.pages:
#             text += page.extract_text()
#         return text

#     def create_embeddings(self, text):
#         sentences = text.split('.')
#         embeddings = self.model.encode(sentences)
#         return sentences, embeddings

#     def store_embeddings_in_neo4j(self, nodes_embeddings):
#         with self.driver.session() as session:
#             for node_id, embedding in nodes_embeddings.items():
#                 session.execute_write(self._create_node_with_embedding, node_id, embedding)
#         self.save_embeddings_to_file(nodes_embeddings)

#     @staticmethod
#     def _create_node_with_embedding(tx, node_id, embedding):
#         tx.run(
#             "CREATE (n:Document {id: $id, embedding: $embedding})",
#             id=node_id, embedding=embedding
#         )

#     def find_similar_nodes(self, query_embedding):
#         with self.driver.session() as session:
#             result = session.run("MATCH (n:Document) RETURN n.id AS id, n.embedding AS embedding")
#             similarities = []
#             for record in result:
#                 node_id = record["id"]
#                 node_embedding = np.array(record["embedding"])
#                 similarity = self._cosine_similarity(query_embedding, node_embedding)
#                 similarities.append((node_id, similarity))
#             return sorted(similarities, key=lambda x: x[1], reverse=True)

#     @staticmethod
#     def _cosine_similarity(vec1, vec2):
#         dot_product = np.dot(vec1, vec2)
#         norm_a = np.linalg.norm(vec1)
#         norm_b = np.linalg.norm(vec2)
#         return dot_product / (norm_a * norm_b)

#     def get_response_from_ollama_llama2(self, prompt):
#         headers = {
#             'Content-Type': 'application/json',
#         }
#         data = {
#             'model': 'llama2',
#             'prompt': prompt
#         }
#         try:
#             with requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data), stream=True) as response:
#                 response.raise_for_status() 
                
#                 result = []
#                 for line in response.iter_lines():
#                     if line:
#                         json_res = json.loads(line.decode('utf-8'))
#                         if 'response' in json_res:
#                             result.append(json_res['response'])
#                             print(json_res['response'], end='', flush=True)
                
#                 final_response = ''.join(result)
#                 return final_response
#         except requests.exceptions.RequestException as e:
#             return f"Error: {e}"
#         except json.JSONDecodeError as e:
#             return f"JSON decode error: {e}"

#     def save_embeddings_to_file(self, nodes_embeddings):
#         file_name = f"{self.db_name}_embeddings.json"
#         with open(file_name, 'w') as file:
#             json.dump(nodes_embeddings, file)
#         print(f"Embeddings saved to {file_name}")

# def main():
#     # Set the database name based on the desired identifier
#     db_name = "my_database_name"

#     # Instantiate VectorEmbeddingManager
#     manager = VectorEmbeddingManager(uri, username, password, db_name)

#     # Extract text from PDF
#     pdf_path = 'Resume.pdf'
#     text = manager.extract_text_from_pdf(pdf_path)
    
#     # Create embeddings
#     sentences, embeddings = manager.create_embeddings(text)
#     nodes_embeddings = {f"doc_{i}": emb.tolist() for i, emb in enumerate(embeddings)}

#     # Store embeddings in Neo4j and save to file
#     manager.store_embeddings_in_neo4j(nodes_embeddings)
    
#     # Ask a question and find relevant sentences
#     question = "Explain the main idea of the document."
#     question_embedding = manager.create_embeddings(question)[1][0]
#     similar_nodes = manager.find_similar_nodes(question_embedding)
    
#     # Generate response from the most similar sentences
#     context = ' '.join([f"Document ID: {node_id}" for node_id, _ in similar_nodes])
#     prompt = f"{context}\n\n{question}"
#     print(f"\nPrompt: {prompt}\n")
#     response = manager.get_response_from_ollama_llama2(prompt)
#     print(f"\nFinal Response: {response}")

# if __name__ == "__main__":
#     main()


import os
import numpy as np
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import requests
import json
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()

# Neo4j connection settings
uri = "bolt://localhost:7687"
username = "neo4j"
password = os.getenv("NEO4J_PASSWORD")

# Ollama API URL
OLLAMA_API_URL = os.getenv("LLM_GENERATE_URL")

class VectorEmbeddingManager:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def extract_text_from_pdf(self, pdf_path):
        reader = PdfReader(pdf_path)
        return ''.join([page.extract_text() for page in reader.pages if page.extract_text()])

    def create_embeddings(self, text):
        sentences = text.split('.')
        embeddings = self.model.encode(sentences)
        return sentences, embeddings

    def store_embeddings_in_neo4j(self, nodes_embeddings):
        with self.driver.session() as session:
            for node_id, embedding in nodes_embeddings.items():
                session.execute_write(self._create_node_with_embedding, node_id, embedding)

    @staticmethod
    def _create_node_with_embedding(tx, node_id, embedding):
        tx.run("CREATE (n:Document {id: $id, embedding: $embedding})", id=node_id, embedding=embedding)

    def find_similar_nodes(self, query_embedding):
        with self.driver.session() as session:
            result = session.run("MATCH (n:Document) RETURN n.id AS id, n.embedding AS embedding")
            similarities = [(record["id"], self._cosine_similarity(query_embedding, np.array(record["embedding"])))
                            for record in result]
            return sorted(similarities, key=lambda x: x[1], reverse=True)

    @staticmethod
    def _cosine_similarity(vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        return dot_product / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    # def get_response_from_ollama_llama2(self, prompt):
    #     headers = {'Content-Type': 'application/json'}
    #     data = {'model': 'llama2', 'prompt': prompt}
    #     try:
    #         response = requests.post(OLLAMA_API_URL, headers=headers, json=data, stream=True)
    #         response.raise_for_status()
    #         result = []
    #         for line in response.iter_lines():
    #             if line:
    #                 json_res = json.loads(line.decode('utf-8'))
    #                 if 'response' in json_res:
    #                     result.append(json_res['response'])
    #         return ''.join(result)
    #     except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
    #         return f"Error: {e}"

    def get_response_from_ollama_llama2(self, prompt):
        headers = {'Content-Type': 'application/json'}
        data = {'model': 'llama2', 'prompt': prompt}
        try:
            response = requests.post(OLLAMA_API_URL, headers=headers, json=data, stream=True)
            response.raise_for_status()
            response_text = []
            
            for line in response.iter_lines():
                if line:
                    try:
                        json_res = json.loads(line.decode('utf-8'))
                        if 'response' in json_res:
                            response_text.append(json_res['response'])
                    except json.JSONDecodeError:
                        continue
            
            return ''.join(response_text)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            return f"Error: {e}"



def main():
    db_name = "my_database_name"
    manager = VectorEmbeddingManager(uri, username, password)

    pdf_path = 'Resume.pdf'
    text = manager.extract_text_from_pdf(pdf_path)
    sentences, embeddings = manager.create_embeddings(text)
    nodes_embeddings = {f"doc_{i}": emb.tolist() for i, emb in enumerate(embeddings)}

    manager.store_embeddings_in_neo4j(nodes_embeddings)

    question = "Explain the main idea of the document."
    question_embedding = manager.create_embeddings(question)[1][0]
    similar_nodes = manager.find_similar_nodes(question_embedding)

    context = ' '.join([f"Document ID: {node_id}" for node_id, _ in similar_nodes])
    prompt = f"{context}\n\n{question}"
    print(f"\nPrompt: {prompt}\n")
    response = manager.get_response_from_ollama_llama2(prompt)
    print(f"\nFinal Response: {response}")

if __name__ == "__main__":
    main()
