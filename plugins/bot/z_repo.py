import asyncio

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ChampuMusic import app
from ChampuMusic.utils.database import add_served_chat, get_assistant


start_txt = """**
✪ 𝐏𝐀𝐇𝐋𝐄 𝐉𝐀 𝐍𝐎𝐁𝐈𝐓𝐀 𝐊𝐎 𝐏𝐀𝐏𝐀 𝐁𝐎𝐋 𝐊𝐄 𝐀𝐀 ✪!
**"""

@app.on_message(filters.command("repo"))
async def start(_, msg):
    buttons = [
        [ 
          InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{app.username}?startgroup=true")
        ],
        [
          InlineKeyboardButton("ɴᴏʙɪᴛᴧ", url="https://t.me/NOBITA_XD1"),
          InlineKeyboardButton("ɴᴏʙɪᴛᴧ ᴋᴧ ʙʜᴧɪ", url="https://t.me/smartness_to_hai"),
          ],
               [
                InlineKeyboardButton("ᴄʜᴧɴɴᴇʟ", url="https://t.me/MUSIC_BOT_UPDATE"),

],[
              InlineKeyboardButton("ᴧʟʟ ʙᴏᴛs", url=f"https://t.me/MUSIC_BOT_UPDATE/377"),
              InlineKeyboardButton("ɢꝛᴏᴜᴘ", url=f"https://t.me/OG_FRAINDS"),
              ],
[
              InlineKeyboardButton("sɪᴍᴘʟᴇ ᴍᴜsɪᴄ", url=f"https://t.me/Nayana_music_bot")
              ],
              [
              InlineKeyboardButton("ᴍᴀɴᴀɢᴍᴇɴᴛ", url=f"https://t.me/shizukaXmusicXrobot"),
InlineKeyboardButton("ᴄʜᴀᴛʙᴏᴛ", url=f"https://t.me/shizukaXmusicXrobot"),
]]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo=config.START_IMG_URL,
        caption=start_txt,
        reply_markup=reply_markup
    )



