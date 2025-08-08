import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMIN_LIST, PINNED_EXEMPT, DELETE_AFTER_SECONDS

# Regex for Telegram links or @mentions
TELEGRAM_LINK_PATTERN = re.compile(r"(t\.me/|telegram\.me/|@[\w\d_]{5,})", re.IGNORECASE)

@Client.on_message(filters.group & ~filters.edited)
async def auto_delete_message(client: Client, message: Message):
    try:
        # Ignore admins
        if message.from_user and message.from_user.id in ADMIN_LIST:
            return

        # Ignore pinned messages
        if PINNED_EXEMPT and getattr(message, "pinned_message", False):
            return

        # Delete immediately if it contains Telegram links or @mentions
        if message.text and TELEGRAM_LINK_PATTERN.search(message.text):
            await message.delete()
            return

        # Delete after 3 minutes
        await asyncio.sleep(DELETE_AFTER_SECONDS)
        await message.delete()
        
    except Exception as e:
        print(f"[AutoDelete] Error: {e}")
