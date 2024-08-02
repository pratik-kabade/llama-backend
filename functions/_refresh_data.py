from crud import Neo4jCRUD

db = Neo4jCRUD()
db.build_from_csv('./data/Alarms.csv')
db.close()