from pyrogram import Client, filters
from pyrogram.types import Message
from database.connections_mdb import get_connected_group
from info import ADMINS
from pyrogram.enums import ChatType

WELCOME_TEXTS = {}

# Check if user is admin in connected group
async def is_admin(client, user_id, chat_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except:
        return False

# /setwelcome command
@Client.on_message(filters.command("setwelcome") & filters.private)
async def set_welcome(client, message: Message):
    connected_chat = await get_connected_group(message.from_user.id)
    if not connected_chat:
        return await message.reply("❌ No group connected. Use /connect in group first.")

    if not await is_admin(client, message.from_user.id, connected_chat):
        return await message.reply("❌ Only group admins can set welcome messages.")

    if len(message.command) < 2:
        return await message.reply("❗ Usage: /setwelcome <your welcome message>")

    WELCOME_TEXTS[connected_chat] = message.text.split(None, 1)[1]
    await message.reply("✅ Welcome message has been set for the group.")

# Send welcome when new member joins
@Client.on_message(filters.new_chat_members)
async def welcome_user(client, message: Message):
    group_id = message.chat.id
    if group_id in WELCOME_TEXTS:
        for user in message.new_chat_members:
            try:
                name = user.mention
                welcome_msg = WELCOME_TEXTS[group_id].replace("{name}", name)
                await message.reply(welcome_msg)
            except Exception as e:
                print(f"Failed to send welcome message: {e}")

# /broadcast command (only in connected group by admin)
@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast(client, message: Message):
    connected_chat = await get_connected_group(message.from_user.id)
    if not connected_chat:
        return await message.reply("❌ No group connected.")

    if not await is_admin(client, message.from_user.id, connected_chat):
        return await message.reply("❌ Only group admins can broadcast messages.")

    if len(message.command) < 2:
        return await message.reply("❗ Usage: /broadcast <message>")

    text = message.text.split(None, 1)[1]
    try:
        await client.send_message(chat_id=connected_chat, text=f"📢 Broadcast:\n\n{text}")
        await message.reply("✅ Broadcast sent.")
    except Exception as e:
        await message.reply(f"❌ Failed to send broadcast: {e}")

# /id command
@Client.on_message(filters.command("id"))
async def get_id(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text(f"👤 Your ID: `{message.from_user.id}`")
    else:
        await message.reply_text(
            f"👥 Group ID: `{message.chat.id}`\n👤 Your ID: `{message.from_user.id}`"
        )
