from crud import Neo4jManager

db = Neo4jManager()
print(db.find_by_property('ADIQ', 'Northings_embedding'))
db.close()