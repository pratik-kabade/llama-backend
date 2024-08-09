from neo4j_manager import Neo4jManager

db = Neo4jManager()
db.delete_all_data('neo4j')
db.close()