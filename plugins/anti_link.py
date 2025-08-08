import re
from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMINS

# Regex to catch:
# - URLs starting with http, https, www
# - @usernames
# - t.me links
LINK_REGEX = r"(https?://\S+|www\.\S+|@\w+|t\.me/\w+)"

@Client.on_message(filters.group & filters.text & ~filters.via_bot)
async def remove_links(client: Client, message: Message):
    if not message.from_user:
        return  # skip if user info is missing

    try:
        # Check if the user is admin in the group
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ("administrator", "creator"):
            return  # Skip if the user is an admin or the group creator
    except Exception as e:
        print(f"[AntiLink] Could not fetch member info: {e}")
        return  # fail-safe: don't delete if status unknown

    if re.search(LINK_REGEX, message.text, flags=re.IGNORECASE):
        try:
            await message.delete()
        except Exception as e:
            print(f"[AntiLink] Failed to delete message: {e}")
