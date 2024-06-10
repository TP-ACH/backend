from motor import motor_asyncio

# MongoDB connection
client = motor_asyncio.AsyncIOMotorClient("mongodb://fastapi:1234@sensor-db:27017/sensor_data?retryWrites=true&w=majority")
db = client.get_database("sensor_data")

def get_collection(collection_name: str):
    return db.get_collection(collection_name)

