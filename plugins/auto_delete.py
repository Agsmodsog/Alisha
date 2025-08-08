import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Time in seconds after which message will be deleted
DELETE_AFTER = 30  # You can change this to any duration

@Client.on_message(filters.group & ~filters.via_bot)
async def auto_delete_messages(client: Client, message: Message):
    if not message.from_user:
        return

    try:
        # Get member status to check if user is admin/creator
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ("administrator", "creator"):
            return  # Skip admins and creator
    except Exception as e:
        print(f"[AutoDelete] Couldn't check admin status: {e}")
        return

    try:
        await asyncio.sleep(DELETE_AFTER)
        await message.delete()
    except Exception as e:
        print(f"[AutoDelete] Failed to delete message: {e}")
