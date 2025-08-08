# database/warning_mdb.py

from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from info import DATABASE_URI, DATABASE_NAME

client = AsyncIOMotorClient(DATABASE_URI)
db = myclient[DATABASE_NAME]
warnings = db["warnings"]

async def add_warn(chat_id: int, user_id: int):
    collection = db["warns"]
    key = {"chat_id": chat_id, "user_id": user_id}
    data = await collection.find_one(key)
    count = data["count"] + 1 if data else 1
    await collection.update_one(key, {"$set": {"count": count}}, upsert=True)
    return count

async def get_warn_count(chat_id: int, user_id: int):
    data = await db["warns"].find_one({"chat_id": chat_id, "user_id": user_id})
    return data["count"] if data else 0

async def reset_warn_count(chat_id: int, user_id: int):
    await db["warns"].delete_one({"chat_id": chat_id, "user_id": user_id})
