from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
load_dotenv()
import os

uri = os.getenv("MONGODB_URL")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client[os.getenv("MONGODB_DB")]