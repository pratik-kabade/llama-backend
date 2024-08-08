from crud import Neo4jManager

db = Neo4jManager()
db.build_from_csv('./data/Alarms.csv')
db.close()