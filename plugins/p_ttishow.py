
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, OWNER_LNK, MELCOW_NEW_USERS, MELCOW_VID, CHNL_LNK, GRP_LNK
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings
from Script import script
from pyrogram.errors import ChatAdminRequired
import asyncio 

"""-----------------------------------------https://t.me/codeflix_bots--------------------------------------"""

@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    r_j_check = [u.id for u in message.new_chat_members]
    if temp.ME in r_j_check:
        if not await db.get_chat(message.chat.id):
            total=await bot.get_chat_members_count(message.chat.id)
            r_j = message.from_user.mention if message.from_user else "Anonymous" 
            await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, r_j))       
            await db.add_chat(message.chat.id, message.chat.title)
        if message.chat.id in temp.BANNED_CHATS:
            # Inspired from a boat of a banana tree
            buttons = [[
                InlineKeyboardButton('• ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ •', url=f'https://t.me/codeflixsupport')
            ]]
            reply_markup=InlineKeyboardMarkup(buttons)
            k = await message.reply(
                text='<b>ᴄʜᴀᴛ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ 🐞\n\nᴍʏ ᴀᴅᴍɪɴꜱ ʜᴀꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ ᴍᴇ ꜰʀᴏᴍ ᴡᴏʀᴋɪɴɢ ʜᴇʀᴇ ! ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ɪᴛ ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ.</b>',
                reply_markup=reply_markup,
            )

            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return
        buttons = [[
                    InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', url='https://telegram.me/codeflixsupport'),
                    InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇꜱ', url='https://telegram.me/codeflix_bots')
                  ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=f"<b>Thankyou For Adding Me In {message.chat.title} ❣️\n\nIf you have any questions & doubts about using me contact support.</b>",
            reply_markup=reply_markup)
    else:
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for u in message.new_chat_members:
                if (temp.MELCOW).get('welcome') is not None:
                    try:
                        await (temp.MELCOW['welcome']).delete()
                    except:
                        pass
                temp.MELCOW['welcome'] = await message.reply_video(
                                                 video=(MELCOW_VID),
                                                 caption=(script.MELCOW_ENG.format(u.mention, message.chat.title)),
                                                 reply_markup=InlineKeyboardMarkup(
                                                                         [[
                                                                           InlineKeyboardButton('• ᴊᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇs •', url='https://t.me/codeflix_bots')
                                                                         ]]
                                                 ),
                                                 parse_mode=enums.ParseMode.HTML
                )
                
        if settings["auto_delete"]:
            await asyncio.sleep(600)
            await (temp.MELCOW['welcome']).delete()
                
               



@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[
                  InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', url='https://telegram.me/codeflixsupport')
                  ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text='<b>ʜᴇʟʟᴏ ꜰʀɪᴇɴᴅꜱ, \nᴍʏ ᴀᴅᴍɪɴ ʜᴀꜱ ᴛᴏʟᴅ ᴍᴇ ᴛᴏ ʟᴇᴀᴠᴇ ꜰʀᴏᴍ ɢʀᴏᴜᴘ, ꜱᴏ ɪ ʜᴀᴠᴇ ᴛᴏ ɢᴏ !/nɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ ᴍᴇ ᴀɢᴀɪɴ ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ.</b>',
            reply_markup=reply_markup,
        )

        await bot.leave_chat(chat)
        await message.reply(f"left the chat `{chat}`")
    except Exception as e:
        await message.reply(f'Error - {e}')

@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat Successfully Disabled')
    try:
        buttons = [[
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', url='https://telegram.me/codeflixsupport')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_, 
            text=f'<b>ʜᴇʟʟᴏ ꜰʀɪᴇɴᴅꜱ, \nᴍʏ ᴀᴅᴍɪɴ ʜᴀꜱ ᴛᴏʟᴅ ᴍᴇ ᴛᴏ ʟᴇᴀᴠᴇ ꜰʀᴏᴍ ɢʀᴏᴜᴘ, ꜱᴏ ɪ ʜᴀᴠᴇ ᴛᴏ ɢᴏ ! \nɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ ᴍᴇ ᴀɢᴀɪɴ ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ..</b> \nReason : <code>{reason}</code>',
            reply_markup=reply_markup)
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat Not Found In DB !")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("Chat Successfully re-enabled")

import psutil  # System resources check karne ke liye
import time

# Function to get uptime
def get_uptime():
    return time.strftime("%H:%M:%S", time.gmtime(time.time() - START_TIME))  # START_TIME ko define karein

@Client.on_message(filters.command('stats') & filters.incoming)
async def get_stats(bot, message):
    if message.from_user.id not in ADMINS:
        m = await message.reply_sticker("CAACAgUAAxkBAAJFeWd037UWP-vgb_dWo55DCPZS9zJzAAJpEgACqXaJVxBrhzahNnwSHgQ")
        await asyncio.sleep(2)
        await m.delete()
        d = await message.reply_sticker(sticker="CAACAgUAAxkBAAJFeWd037UWP-vgb_dWo55DCPZS9zJzAAJpEgACqXaJVxBrhzahNnwSHgQ")
        await asyncio.sleep(15)
        await d.delete()
    else:
        rju = await message.reply('Fetching stats...')
        print("✅ Step 1: Bot received /stats command")

        # Database se values fetch kar rahe hain
        try:
            total_users = await db.total_users_count()
            print(f"✅ Step 2: Total Users Fetched: {total_users}")

            total_chats = await db.total_chat_count()
            print(f"✅ Step 3: Total Chats Fetched: {total_chats}")

            premium_users = await db.premium_users_count()
            print(f"✅ Step 4: Premium Users Fetched: {premium_users}")

            files = await Media.count_documents()
            print(f"✅ Step 5: Total Files Fetched: {files}")

            size = await db.get_db_size()
            free = 536870912 - size
            size = get_size(size)
            free = get_size(free)
            print(f"✅ Step 6: Database size fetched: {size}, Free Space: {free}")

            # Database 2 ka stats
            db2_files = await db2.total_files_count()
            db2_size = await db2.get_db_size()
            db2_free = 536870912 - db2_size
            db2_size = get_size(db2_size)
            db2_free = get_size(db2_free)
            print(f"✅ Step 7: DB2 Files: {db2_files}, Size: {db2_size}, Free: {db2_free}")

            # System Stats
            bot_uptime = get_bot_uptime()
            print(f"✅ Step 8: Bot Uptime: {bot_uptime}")

            ram_usage = get_ram_usage()
            cpu_usage = get_cpu_usage()
            print(f"✅ Step 9: RAM: {ram_usage}%, CPU: {cpu_usage}%")

            # Dono databases ki total files
            total_files_both_dbs = files + db2_files
            print(f"✅ Step 10: Total Files (Both DBs): {total_files_both_dbs}")

            # Message edit karein sahi data ke saath
            await rju.edit(script.STATUS_TXT.format(
                total_users, total_chats, premium_users, files, size, free,
                db2_files, db2_size, db2_free,
                bot_uptime, ram_usage, cpu_usage,
                total_files_both_dbs
            ))
            print("✅ Step 11: Stats message edited successfully!")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            await rju.edit(f"❌ Error fetching stats: {e}")

@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply("Invite Link Generation Failed, Iam Not Having Sufficient Rights")
    except Exception as e:
        return await message.reply(f'Error {e}')
    await message.reply(f'Here is your Invite Link {link.invite_link}')

@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    # https://t.me/GetTGLink/4185
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure I have met him before.")
    except IndexError:
        return await message.reply("This might be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} is already banned\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"Successfully banned {k.mention}")


    
@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("Thismight be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"Successfully unbanned {k.mention}")


    
@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    # https://t.me/GetTGLink/4184
    raju = await message.reply('Getting List Of Users')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += '( Banned User )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users")

@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('Getting List Of chats')
    chats = await db.get_all_chats()
    out = "Chats Saved In DB Are:\n\n"
    async for chat in chats:
        out += f"**Title:** `{chat['title']}`\n**- ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            out += '( Disabled Chat )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="List Of Chats")
