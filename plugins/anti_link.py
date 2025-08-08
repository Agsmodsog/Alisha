from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message
from info import ADMINS, LOG_CHANNEL

import re

# URL detection regex
URL_REGEX = r"(https?://|www\.)[^\s]+"

@Client.on_message(filters.group)
async def delete_links_in_group(client: Client, message: Message):
    # Skip if from admin or pinned message
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id

        # Get member status
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return  # Skip admins

        # Skip pinned messages
        if message.pinned_message:
            return

        # Check for links in text, caption, or entities
        text_to_check = message.text or message.caption or ""
        if re.search(URL_REGEX, text_to_check):
            await message.delete()

            log_msg = (
                f"🚫 **Link Deleted**\n"
                f"👤 User: [{message.from_user.first_name}](tg://user?id={user_id}) (`{user_id}`)\n"
                f"💬 Group: {message.chat.title} (`{chat_id}`)\n"
                f"🗑️ Message with link was deleted."
            )

            # Notify admins
            for admin_id in ADMINS:
                try:
                    await client.send_message(admin_id, log_msg)
                except Exception as e:
                    print(f"Failed to notify admin {admin_id}: {e}")

            # Notify log channel
            try:
                await client.send_message(LOG_CHANNEL, log_msg)
            except Exception as e:
                print(f"Failed to send to log channel: {e}")

    except Exception as e:
        print(f"Error in delete_links_in_group: {e}")
