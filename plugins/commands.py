import os,logging,random,asyncio,re,json,base64,tgcrypto
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid, FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton,CallbackQuery
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp
from database.connections_mdb import active_connection
logger = logging.getLogger(__name__)

REACTIONS = ["🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩", "😱", "🤣", "😘", "👏", "😛", "😈", "🎉", "⚡️", "🫡", "🤓", "😎", "🏆", "🔥", "🤭", "🌚", "🆒", "👻", "😁","🤍","🎊"] #don't add any emoji because tg not support all emoji reactions


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message: Message):
    user_id = message.from_user.id

    # React with a random emoji from the list
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass

    # Group start
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [InlineKeyboardButton('⤬ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')],
            [InlineKeyboardButton('📢 ᴏᴛᴛ ᴜᴘᴅᴀᴛᴇ 📢', url="https://t.me/+RDsxY-lQ55wwOWI1")],
            [InlineKeyboardButton('🧩 ʙᴏᴛ ᴜᴘᴅᴀᴛᴇ 🧩', url="https://t.me/AgsModsOG")],
            [InlineKeyboardButton('🎊 ᴍᴏᴠɪᴇ ᴄʜᴀɴɴᴇʟ 🎊', url="https://t.me/+RDsxY-lQ55wwOWI1")]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply(
            script.START_TXT.format(
                message.from_user.mention if message.from_user else message.chat.title,
                temp.U_NAME,
                temp.B_NAME
            ),
            reply_markup=reply_markup
        )
        await asyncio.sleep(1)
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown")
            )
            await db.add_chat(message.chat.id, message.chat.title)
        return

    # Private start
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention)
        )

    # No start parameter
    if len(message.command) != 2:
        loading_msg = await message.reply_sticker("CAACAgUAAxkBAAEBfxNojk--UvtbpB5AiG9bDdYw4EOFMwACGxkAAvHLcVTiDQsdjHCtZjYE") 
        await asyncio.sleep(0.2)
        await loading_msg.edit("✅ **Process Complete! Welcome to the Bot.**")
        await asyncio.sleep(1)
        await loading_msg.delete()

        # Show main menu buttons
        buttons = [
            [InlineKeyboardButton('⤬ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')],
            [InlineKeyboardButton('📢 ᴏᴛᴛ ᴜᴘᴅᴀᴛᴇ 📢', url="https://t.me/+RDsxY-lQ55wwOWI1")],
            [InlineKeyboardButton('🧩 ʙᴏᴛ ᴜᴘᴅᴀᴛᴇ 🧩', url="https://t.me/AgsModsOG")],
            [InlineKeyboardButton('🎊 ᴍᴏᴠɪᴇ ᴄʜᴀɴɴᴇʟ 🎊', url="https://t.me/+RDsxY-lQ55wwOWI1")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    # Start parameter handling continues below..
    invite_links = await is_subscribed(client, query=message)
    if AUTH_CHANNEL and len(invite_links) >= 1:
        #this is written by tg: @programcrasher
        btn = []
        for chnl_num, link in enumerate(invite_links, start=1):
            if chnl_num == 1:
                channel_num = "1sᴛ"
            elif chnl_num == 2:
                channel_num = "2ɴᴅ"
            elif chnl_num == 3:
                channel_num = "3ʀᴅ"
            else:
                channel_num = str(chnl_num)+"ᴛʜ"
            btn.append([
                InlineKeyboardButton(f"❆ Jᴏɪɴ {channel_num} Cʜᴀɴɴᴇʟ ❆", url=link)
            ])

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        authdel=await client.send_message(
            chat_id=message.from_user.id,
            text="**Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟs ɢɪᴠᴇɴ ʙᴇʟᴏᴡ sᴏ ʏᴏᴜ ᴅᴏɴ'ᴛ ɢᴇᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ...\n\nIғ ʏᴏᴜ ᴡᴀɴᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ɢɪᴠᴇɴ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴀɴᴅ ᴊᴏɪɴ ᴏᴜʀ ʙᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟs, ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ '↻ Tʀʏ Aɢᴀɪɴ' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ...\n\nTʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇs...**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        await asyncio.sleep(25)
        await authdel.delete()
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [
            [InlineKeyboardButton('⤬ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')],
            [InlineKeyboardButton('📢 ᴏᴛᴛ ᴜᴘᴅᴀᴛᴇ 📢', url="https://t.me/+RDsxY-lQ55wwOWI1")],
            [InlineKeyboardButton('🧩 ʙᴏᴛ ᴜᴘᴅᴀᴛᴇ 🧩', url="https://t.me/AgsModsOG")],
            [InlineKeyboardButton('🎊 ᴍᴏᴠɪᴇ ᴄʜᴀɴɴᴇʟ 🎊', url="https://t.me/+RDsxY-lQ55wwOWI1")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
