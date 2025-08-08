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

BATCH_FILES = {}

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
            [InlineKeyboardButton('♻ ᴅᴇᴠᴇʟᴏᴘᴇʀ ♻', url="https://t.me/AgsModsOG")],
            [InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
             InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')]
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
            [InlineKeyboardButton('♻ ᴅᴇᴠᴇʟᴏᴘᴇʀ ♻', url="https://t.me/AgsModsOG1")],
            [InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
             InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')]
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
            [InlineKeyboardButton('♻ ᴅᴇᴠᴇʟᴏᴘᴇʀ ♻', url="https://t.me/AgsModsOG")],
            [InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
             InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 
    if data == "start":
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton('♻ ᴅᴇᴠᴇʟᴏᴘᴇʀ ♻', url="https://t.me/AgsModsOG"),
                InlineKeyboardButton('• ʜᴇʟᴘ •', callback_data='help')],
                [InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')]
            ])
        )
    elif data == "help":
        await query.message.edit_text(
            text=script.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("About", callback_data = "about")],
                [InlineKeyboardButton("ʜᴏᴍᴇ", callback_data = "start")]
            ])            
        )

    elif data == "about":
        await query.message.edit_text(
            text=script.ABOUT_TXT,
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Help", callback_data='help')],
                [InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="start")]
            ])            
        )


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer('Piracy Is Crime')
    await message.message.edit('Succesfully Deleted All The Indexed Files.')


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    settings = await get_settings(grp_id)

    if settings is not None:
        buttons = [
        
            [
                InlineKeyboardButton(
                    'IMDB',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["imdb"] else '❌ No',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            
            [
                InlineKeyboardButton(
                    'Welcome',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["welcome"] else '❌ No',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=f"<b>Change Your Settings for {title} As Your Wish ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )

@Client.on_callback_query(filters.regex("checkfsub"))
async def recheck_subscription(client, callback_query):
    user_id = callback_query.from_user.id
    message = callback_query.message
    
    try:
        # Check membership in FORCE_SUB_1
        member1 = await client.get_chat_member(FORCE_SUB_1, user_id)
        if member1.status == "kicked":
            await callback_query.answer("🚫 You are banned from accessing this bot (Channel 1).", show_alert=True)
            return
    except UserNotParticipant:
        # If user is not a member of FORCE_SUB_1
        await callback_query.answer("❌ You must join the Main Channel 1 to proceed.", show_alert=True)
        return
    
    try:
        # Check membership in FORCE_SUB_2
        member2 = await client.get_chat_member(FORCE_SUB_2, user_id)
        if member2.status == "kicked":
            await callback_query.answer("🚫 You are banned from accessing this bot (Channel 2).", show_alert=True)
            return
    except UserNotParticipant:
        # If user is not a member of FORCE_SUB_2
        await callback_query.answer("❌ You must join the Main Channel 2 to proceed.", show_alert=True)
        return
    
    # If user is in both channels, restart the start function
    await start(client, message)

