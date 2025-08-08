import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMINS, PINNED_EXEMPT, DELETE_AFTER_SECONDS


@Client.on_message(filters.group & ~filters.edited)
async def auto_delete_message(client: Client, message: Message):
    try:
        # Ignore admins
        if message.from_user and message.from_user.id in ADMINS:
            return

        # Ignore pinned messages
        if PINNED_EXEMPT and getattr(message, "pinned_message", False):
            return


        # Delete after 3 minutes
        await asyncio.sleep(DELETE_AFTER_SECONDS)
        await message.delete()
        
    except Exception as e:
        print(f"[AutoDelete] Error: {e}")
