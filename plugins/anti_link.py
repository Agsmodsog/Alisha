import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMINS, LOG_CHANNEL
from database.users_chats_db import add_user

# Dictionary to store warning counts
user_warnings = {}

# Link detection pattern
link_pattern = re.compile(r"(https?://|www\.)\S+")

# Check if user is admin
async def is_admin(client: Client, message: Message):
    member = await message.chat.get_member(message.from_user.id)
    return member.status in ["administrator", "creator"]

# Check if bot is admin
async def bot_is_admin(client: Client, message: Message):
    bot = await message.chat.get_member(client.me.id)
    return bot.status == "administrator"

@Client.on_message(filters.group & filters.text, group=1)
async def delete_link(client, message: Message):
    if not await bot_is_admin(client, message):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text

    # Don't process if user is admin
    if await is_admin(client, message):
        return

    # If link detected
    if link_pattern.search(text):
        try:
            await message.delete()
        except:
            pass

        user_warnings.setdefault((chat_id, user_id), 0)
        user_warnings[(chat_id, user_id)] += 1
        count = user_warnings[(chat_id, user_id)]

        warn_text = f"⚠️ Warning {count}/3: Sending links is not allowed!"
        await message.reply_text(warn_text, quote=True)

        # Kick after 3 warnings
        if count >= 3:
            try:
                await client.kick_chat_member(chat_id, user_id)
                user_warnings.pop((chat_id, user_id))

                log_text = f"🚫 User [{message.from_user.first_name}](tg://user?id={user_id}) was kicked for sending links 3 times in {message.chat.title}."
                for admin_id in ADMINS:
                    try:
                        await client.send_message(admin_id, log_text)
                    except:
                        pass
                await client.send_message(LOG_CHANNEL, log_text)
            except:
                pass

@Client.on_message(filters.group, group=2)
async def auto_delete_messages(client, message: Message):
    if not await bot_is_admin(client, message):
        return

    # Skip admin messages and pinned messages
    if await is_admin(client, message) or message.pinned_message:
        return

    # Delete message after 180 seconds (3 minutes)
    await asyncio.sleep(180)
    try:
        await message.delete()
    except:
        pass

@Client.on_chat_member_updated(filters.group, group=3)
async def notify_admin_on_ban(client, member_update):
    if not await bot_is_admin(client, member_update):
        return

    old_status = member_update.old_chat_member.status
    new_status = member_update.new_chat_member.status
    user = member_update.new_chat_member.user

    # If member is kicked or banned
    if old_status in ["member", "restricted"] and new_status in ["kicked", "banned"]:
        msg = f"🚨 User [{user.first_name}](tg://user?id={user.id}) was removed from **{member_update.chat.title}**."

        for admin_id in ADMINS:
            try:
                await client.send_message(admin_id, msg)
            except:
                pass
        await client.send_message(LOG_CHANNEL, msg)
