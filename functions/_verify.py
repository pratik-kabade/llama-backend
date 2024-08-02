from crud import Neo4jCRUD

db = Neo4jCRUD()
print(db.find_by_property('ADIQ', 'Northings_embedding'))
db.close()