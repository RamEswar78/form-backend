"""
MongoDB connection setup for FastAPI using Motor (async MongoDB driver).
Install with: pip install motor
"""

from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "your_database_name"

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

# Example FastAPI dependency to get the database
async def get_database():
    return db

# Usage in FastAPI endpoint:
# from fastapi import Depends
# @app.get("/items")
# async def get_items(db=Depends(get_database)):
#     items = await db["items"].find().to_list(100)
#     return items
