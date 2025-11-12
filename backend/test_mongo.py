from pymongo import MongoClient
import certifi, os
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri, tlsCAFile=certifi.where())
print("Databases:", client.list_database_names())
