import re
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, ChatMemberUpdated
from info import ADMINS, LOG_CHANNEL
from database.warn_db import add_warn, get_warn_count, reset_warn_count

link_regex = re.compile(r"(https?://\S+|t\.me/\S+|telegram\.me/\S+)", re.IGNORECASE)

@Client.on_message(filters.group & filters.text & ~filters.private)
async def anti_link_checker(client: Client, message: Message):
    if not message.from_user or message.sender_chat:
        return

    user = message.from_user
    chat_id = message.chat.id
    user_id = user.id

    if message.text and link_regex.search(message.text):
        member = await client.get_chat_member(chat_id, user_id)

        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            try:
                await message.delete()
            except Exception:
                pass

            warn_count = await add_warn(chat_id, user_id)

            if warn_count >= 3:
                try:
                    await client.ban_chat_member(chat_id, user_id)
                    await message.reply_text(
                        f"🚫 [{user.first_name}](tg://user?id={user.id}) banned for repeated link sharing.",
                        disable_web_page_preview=True
                    )

                    log_msg = (
                        f"🚫 **User Banned for Link Spam**\n\n"
                        f"👤 User: [{user.first_name}](tg://user?id={user.id}) (`{user.id}`)\n"
                        f"💬 Group: {message.chat.title} (`{chat_id}`)\n"
                        f"📛 Reason: 3x link spam"
                    )

                    for admin_id in ADMINS:
                        try:
                            await client.send_message(admin_id, log_msg)
                        except Exception:
                            pass

                    await client.send_message(LOG_CHANNEL, log_msg)
                    await reset_warn_count(chat_id, user_id)
                except Exception as e:
                    print(f"Error banning user {user_id}: {e}")
            else:
                await message.reply_text(
                    f"⚠️ Link sharing is not allowed!\n"
                    f"Warning {warn_count}/3 for [{user.first_name}](tg://user?id={user.id}).",
                    disable_web_page_preview=True
                )

@Client.on_chat_member_updated()
async def member_kicked_or_banned(client: Client, chat_member: ChatMemberUpdated):
    old = chat_member.old_chat_member
    new = chat_member.new_chat_member
    chat = chat_member.chat
    user = new.user

    if (
        old.status not in [ChatMemberStatus.BANNED, ChatMemberStatus.KICKED]
        and new.status in [ChatMemberStatus.BANNED, ChatMemberStatus.KICKED]
    ):
        message = (
            f"🚫 **Member Removed**\n\n"
            f"👤 User: [{user.first_name}](tg://user?id={user.id}) (`{user.id}`)\n"
            f"💬 Group: {chat.title} (`{chat.id}`)\n"
            f"📛 Status: {new.status.capitalize()}"
        )

        for admin_id in ADMINS:
            try:
                await client.send_message(admin_id, message)
            except Exception as e:
                print(f"Failed to notify admin {admin_id}: {e}")

        try:
            await client.send_message(LOG_CHANNEL, message)
        except Exception as e:
            print(f"Failed to send log to LOG_CHANNEL: {e}")

@Client.on_message(filters.group & ~filters.service)
async def auto_delete_after_delay(client: Client, message: Message):
    if message.pinned:
        return

    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
    except:
        return

    await asyncio.sleep(180)  # 3 minutes
    try:
        await message.delete()
    except:
        pass
