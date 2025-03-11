import logging
import asyncio
import re
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import ADMINS, INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()


@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    print("✅ Index command received!")  # Debugging
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")

    _, action, chat, lst_msg_id, from_user = query.data.split("#")
    
    if action == 'reject':
        await query.message.delete()
        await bot.send_message(int(from_user),
                               f'Your submission for indexing {chat} has been declined by moderators.',
                               reply_to_message_id=int(lst_msg_id))
        return

    if lock.locked():
        return await query.answer('Wait until the previous process completes.', show_alert=True)
    
    msg = query.message
    await query.answer('Processing...⏳', show_alert=True)

    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               f'Your submission for indexing {chat} has been accepted by moderators and will be added soon.',
                               reply_to_message_id=int(lst_msg_id))

    await msg.edit(
        "Starting Indexing...",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
        )
    )

    try:
        chat = int(chat)
    except ValueError:
        pass

    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


@Client.on_message((filters.forwarded | (filters.regex(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text ) & filters.private & filters.incoming)
async def send_for_index(bot, message):
    print("✅ Index request received!")  # Debugging

    if message.text:
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('Invalid link')

        chat_id = match.group(4)
        last_msg_id = int(match.group(5))

        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)
    
    elif message.forward_from_chat and message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return await message.reply("Could not fetch the chat details. Try again.")

    try:
        await bot.get_chat(chat_id)
    except (ChannelInvalid, UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid or private channel/group. Make me an admin to index files.')
    except Exception as e:
        logger.exception(e)
        return await message.reply(f'Error - {e}')

    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except Exception:
        return await message.reply('Ensure I am an admin in the channel if it is private.')

    if k.empty:
        return await message.reply('This might be a group, and I am not an admin.')

    if message.from_user.id in ADMINS:
        buttons = [
            [InlineKeyboardButton('Yes', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
            [InlineKeyboardButton('Close', callback_data='close_data')]
        ]
        return await message.reply(
            f'Do you want to index this chat?\n\nChat ID: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>',
            reply_markup=InlineKeyboardMarkup(buttons))

    try:
        link = (await bot.create_chat_invite_link(chat_id)).invite_link if type(chat_id) is int else f"@{message.forward_from_chat.username}"
    except ChatAdminRequired:
        return await message.reply('Ensure I am an admin and can create invite links.')

    buttons = [
        [InlineKeyboardButton('Accept Index', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
        [InlineKeyboardButton('Reject Index', callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}')]
    ]

    await bot.send_message(LOG_CHANNEL,
                           f'#IndexRequest\n\nBy: {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>\nInvite Link: {link}',
                           reply_markup=InlineKeyboardMarkup(buttons))

    await message.reply('Thank you for the contribution. Moderators will verify the files.')


@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    try:
        _, skip = message.text.split(" ")
        temp.CURRENT = int(skip)
        await message.reply(f"Successfully set SKIP number to {skip}")
    except ValueError:
        await message.reply("Invalid input. Please provide a valid number.")


async def index_files_to_db(lst_msg_id, chat, msg, bot):
    total_files, duplicate, errors, deleted, no_media, unsupported = 0, 0, 0, 0, 0, 0
    
    async with lock:
        try:
            temp.CANCEL = False
            current = temp.CURRENT
            
            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
                if temp.CANCEL:
                    return await msg.edit(f"Indexing Cancelled.\n\nTotal Files Indexed: {total_files}\nDuplicates Skipped: {duplicate}\nDeleted Messages: {deleted}\nNon-Media Skipped: {no_media + unsupported} (Unsupported: {unsupported})\nErrors: {errors}")

                current += 1
                if current % 50 == 0:
                    await msg.edit_text(
                        text=f"Fetched: <code>{current}</code>\nSaved: <code>{total_files}</code>\nDuplicates: <code>{duplicate}</code>",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Cancel', callback_data='index_cancel')]])
                    )

                if message.empty:
                    deleted += 1
                elif not message.media:
                    no_media += 1
                elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                    unsupported += 1
                else:
                    media = getattr(message, message.media.value, None)
                    if not media:
                        unsupported += 1
                    else:
                        media.file_type = message.media.value
                        media.caption = message.caption
                        saved, status = await save_file(bot, media)
                        if saved:
                            total_files += 1
                        elif status == 0:
                            duplicate += 1
                        elif status == 2:
                            errors += 1
                        
            await msg.edit(f"Indexing Complete! {total_files} files saved. Errors: {errors}")

        except Exception as e:
            logger.exception(e)
            await msg.edit(f'Error: {e}')
