import os
from neo4j_manager import Neo4jManager

username = os.getenv("NEO4J_USER", 'neo4j')
password = os.getenv("NEO4J_PASSWORD", 'genesis')
uri = os.getenv("NEO4J_URI", 'bolt://localhost:7687')
base_uri = os.getenv("NEO4J_BASEURL", 'http://localhost:7474')
llm_model = os.getenv("LLM_MODEL", 'llama2')

db = Neo4jManager(username, password, uri, base_uri, llm_model)
db.get_database_data('neo4j')
db.close()