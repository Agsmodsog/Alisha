import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from info import *



@Client.on_message(filters.group & ~filters.edited)
async def auto_delete_message(client: Client, message: Message):
    try:
        # Skip if it's from an admin
        if message.from_user and message.from_user.id in ADMIN_LIST:
            return

        # Skip pinned messages
        if PINNED_EXEMPT and message.pinned_message:
            return

        # Wait and delete
        await asyncio.sleep(DELETE_AFTER_SECONDS)
        await message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")
