from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/") # A Decommenter si vous voulez executer en local et commenter la ligne suivante
#client = MongoClient("mongodb://mongodb:27017/")  # Utiliser le nom de service Docker pour MongoDB
db = client.operation_db

def get_db():
    return db
