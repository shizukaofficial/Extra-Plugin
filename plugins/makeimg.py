from pyrogram import Client, filters, enums
from lexica import Client as ApiClient, AsyncClient
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, InputMediaPhoto
from math import ceil
import asyncio
from ChampuMusic import app

api = ApiClient()
Models = api.getModels()['models']['image']

Database = {}

async def ImageGeneration(model, prompt):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://deepdreamgenerator.com/api/generate",
                json={"model": model, "prompt": prompt},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "success":
                        return data["image_url"]
                    else:
                        raise Exception(f"Failed to generate image: {data['error']}")
                else:
                    raise Exception(f"Failed to generate image: {response.status}")
    except Exception as e:
        raise Exception(f"Failed to generate the image: {e}")
    finally:
        await session.close()

def getText(message):
    """Extract Text From Commands"""
    text_to_return = message.text
    if message.text is None:
        return None
    if " " in text_to_return:
        try:
            return message.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None

class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text

def paginate_models(page_n: int, models: list, user_id) -> list:
    modules = sorted(
        [
            EqInlineKeyboardButton(
                x['name'],
                callback_data=f"d.{x['id']}.{user_id}"
            )
            for x in models
        ]
    )

    pairs = list(zip(modules[::3], modules[1::3]))
    i = 0
    for m in pairs:
        for _ in m:
            i += 1
    if len(modules) - i == 1:
        pairs.append((modules[-1],))
    elif len(modules) - i == 2:
        pairs.append(
            (
                modules[-2],
                modules[-1],
            )
        )

    COLUMN_SIZE = 3

    max_num_pages = ceil(len(modules) / COLUMN_SIZE)

    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > COLUMN_SIZE:
        pairs = pairs[
            modulo_page * COLUMN_SIZE: COLUMN_SIZE * (modulo_page + 1)
        ] + [
            (
                EqInlineKeyboardButton(
                    "◁",
                    callback_data=f"d.left.{modulo_page}.{user_id}"
                ),
                EqInlineKeyboardButton(
                    "⌯ ᴄᴀɴᴄᴇʟ ⌯",
                    callback_data=f"close_data"
                ),
                EqInlineKeyboardButton(
                    "▷",
                    callback_data=f"d.right.{modulo_page}.{user_id}"
                ),
            )
        ]
    else:
        pairs += [[EqInlineKeyboardButton("⌯ ʙᴀᴄᴋ ⌯", callback_data=f"d.-1.{user_id}")]]

    return pairs

@app.on_message(filters.command(["draw", "create", "imagine", "dream"]))
async def draw(_: app, m: Message):
    global Database
    if len(m.command) == 1:
        return await m.reply_text("Please provide a prompt. Usage: `/draw <prompt>`", parse_mode=enums.ParseMode.MARKDOWN)
    prompt = getText(m)
    user = m.from_user
    data = {'prompt': prompt, 'reply_to_id': m.id}
    Database[user.id] = data
    btns = paginate_models(0, Models, user.id)
    await m.reply_text(
        text=f"**Hello {m.from_user.mention}**\n\n**Select your image generator model**",
        reply_markup=InlineKeyboardMarkup(btns)
    )

@app.on_callback_query(filters.regex(pattern=r"^d.(.*)"))
async def selectModel(_: app, query: CallbackQuery):
    global Database
    data = query.data.split('.')
    auth_user = int(data[-1])
    if query.from_user.id != auth_user:
        return await query.answer("No.")
    if len(data) > 3:
        if data[1] == "right":
            next_page = int(data[2])
            await query.edit_message_reply_markup(
                InlineKeyboardMarkup(
                    paginate_models(next_page + 1, Models, auth_user)
                )
            )
        elif data[1] == "left":
            next_page = int(data[2])
            await query.edit_message_reply_markup(
                InlineKeyboardMarkup(
                    paginate_models(next_page - 1, Models, auth_user)
                )
            )
    else:
        model_id = data[1]
        model = [x for x in Models if x['id'] == model_id][0]
        user_data = Database[auth_user]
        try:
            image_url = await ImageGeneration(model['name'], user_data['prompt'])
            await query.edit_message_media(
                InputMediaPhoto(image_url)
            )
            await query.edit_message_reply_markup(
                InlineKeyboardMarkup(
                    [
                        [
                            EqInlineKeyboardButton(
                                "⌯ ᴄʟᴏsᴇ ⌯",
                                callback_data=f"close_data"
                            )
                        ]
                    ]
                )
            )
        except Exception as e:
        await query.answer(f"Failed to generate image: {e}")

@app.on_callback_query(filters.regex(pattern=r"^close_data"))
async def close_data(_: app, query: CallbackQuery):
    await query.edit_message_reply_markup(
        InlineKeyboardMarkup(
            [
                [
                    EqInlineKeyboardButton(
                        "⌯ ᴄʟᴏsᴇ ⌯",
                        callback_data=f"close_data"
                    )
                ]
            ]
        )
    )
    await query.answer("Closed")