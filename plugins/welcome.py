from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
from Script import *
from info import *

# Only react to group join events
@Client.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client: Client, message: Message):
    for user in message.new_chat_members:
        try:
            # Skip admins if needed (optional)
            member = await client.get_chat_member(message.chat.id, user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                continue

            # Send welcome message with image
            caption = WELCOME_TEXTS.format(
                mention=user.mention,
                chat=message.chat.title,
                user_id=user.id
            )
            await message.reply_photo(photo=WELCOME_IMAGE, caption=caption)

        except Exception as e:
            print(f"Failed to send welcome message: {e}")
