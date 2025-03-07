from database.mongodb.mongodb import MongoManager
from config import settings

mongo_client = MongoManager(settings.mongodb_timenest_db_name)



mongo_client.insert_one(
    "knowledge",
    {
        "title": 'hello world'    
    }
)
print(mongo_client.find(
    "knowledge"
))