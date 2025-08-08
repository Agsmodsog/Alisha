# database/warning_mdb.py

from motor.motor_asyncio import AsyncIOMotorClient
import os
from info import DATABASE_URI, DATABASE_NAME

client = AsyncIOMotorClient(DATABASE_URI)
db = myclient[DATABASE_NAME]]
warnings = db["warnings"]

async def warn_user(group_id: int, user_id: int) -> int:
    doc = await warnings.find_one({"group_id": group_id, "user_id": user_id})
    if doc:
        new_count = doc["count"] + 1
        await warnings.update_one(
            {"group_id": group_id, "user_id": user_id},
            {"$set": {"count": new_count}}
        )
    else:
        new_count = 1
        await warnings.insert_one({"group_id": group_id, "user_id": user_id, "count": 1})
    return new_count

async def clear_warnings(group_id: int, user_id: int):
    await warnings.delete_one({"group_id": group_id, "user_id": user_id})
