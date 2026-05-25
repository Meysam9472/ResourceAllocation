from pymongo import MongoClient
from contextlib import contextmanager
from dotenv import load_dotenv
import os
from database import AsyncSessionLocal


load_dotenv()

@contextmanager
def get_mongo_connection():
    MONGO_URI = os.getenv("MONGO_DB_URI")
    client = MongoClient(MONGO_URI)
    try:
        yield client
    finally:
        client.close()


async def get_postgres_db_connection():
    with AsyncSessionLocal as session:
        yield session