from pymongo import MongoClient
from contextlib import contextmanager


@contextmanager
def get_mongo_connection():
    # MongoDB connection URI
    MONGO_URI = "mongodb://localhost:27017/"
    client = MongoClient(MONGO_URI)
    try:
        yield client
    finally:
        client.close()