import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMember

# Time (in seconds) before deletion
DELETE_AFTER = 60

async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member: ChatMember = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception as e:
        print(f"[AutoDelete] Failed to get chat member: {e}")
        return False


@Client.on_message(filters.text & ~filters.via_bot)
async def auto_delete_text(client: Client, message: Message):
    try:
        # If private chat → delete all text after 60s
        if message.chat.type == "private":
            await asyncio.sleep(DELETE_AFTER)
            await message.delete()

        # If group/supergroup → delete text unless from admin
        elif message.chat.type in ["group", "supergroup"]:
            if await is_admin(client, message.chat.id, message.from_user.id):
                return  # Don't delete admin messages
            await asyncio.sleep(DELETE_AFTER)
            await message.delete()

    except Exception as e:
        print(f"[AutoDelete] Error: {e}")
