from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "")
print(MONGODB_URI)
print(MONGODB_DB)


# Initialize the client once
client = MongoClient(MONGODB_URI)

# Get the database object
mongo = client[MONGODB_DB]

