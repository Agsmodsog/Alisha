from pyrogram import Client, filters
from pyrogram.types import Message
import re

# Regular expression to match links
LINK_REGEX = r"(https?://\S+|www\.\S+)"

# Filters incoming messages for links
@Client.on_message(filters.group & filters.text & ~filters.via_bot)
async def remove_links(client: Client, message: Message):
    if re.search(LINK_REGEX, message.text):
        try:
            await message.delete()
        except Exception as e:
            print(f"Failed to delete message with link: {e}")
