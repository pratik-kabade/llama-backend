from neo4j_manager import Neo4jManager

db = Neo4jManager()
db.get_database_data('neo4j')
db.close()