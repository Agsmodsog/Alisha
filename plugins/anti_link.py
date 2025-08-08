import re
from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMIN

# Regex to catch:
# - URLs starting with http, https, www
# - @usernames
# - t.me links
LINK_REGEX = r"(https?://\S+|www\.\S+|@\w+|t\.me/\w+)"

@Client.on_message(filters.group & filters.text & ~filters.via_bot)
async def remove_links(client: Client, message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    if user_id in ADMIN_LIST:
        return  # Don't delete messages from admins

    if re.search(LINK_REGEX, message.text, flags=re.IGNORECASE):
        try:
            await message.delete()
        except Exception as e:
            print(f"[AntiLink] Failed to delete message: {e}")
