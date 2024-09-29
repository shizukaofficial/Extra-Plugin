import base64
import httpx
import os
import config
from ChampuMusic import app
from pyrogram import Client, filters
import pyrogram
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiofiles
import aiohttp
import requests
from lexica import create_api
# Initialize Lexica API
lexica_api = create_api()

async def image_loader(image: str, link: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            if resp.status == 200:
                f = await aiofiles.open(image, mode="wb")
                await f.write(await resp.read())
                await f.close()
                return image
            return image

@app.on_message(filters.command("upscale", prefixes="/"))
async def upscale_image(client, message):
    chat_id = message.chat.id
    replied = message.reply_to_message
    if not replied:
        return await message.reply_text("Please Reply To An Image ...")
    if not replied.photo:
        return await message.reply_text("Please Reply To An Image ...")

    aux = await message.reply_text("Please Wait ...")
    image_path = await replied.download()

    try:
        # Convert the image to a base64 string to send as a prompt
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Generate a new image using Lexica API with the original image as a prompt
        response = lexica_api.generate_images(prompt=f"Upscale this image: {encoded_image}", limit=1)

        if response and response['images']:
            upscaled_image_url = response['images'][0]['url']
            downloaded_image = await image_loader(image_path, upscaled_image_url)
            await aux.delete()
            return await message.reply_document(downloaded_image)
        else:
            await aux.edit_text("Failed to generate the upscaled image.")
    except Exception as e:
        await aux.edit_text(f"An unexpected error occurred: {str(e)}")

# ------------

@app.on_message(filters.command("waifu"))
async def waifu_command(client, message):
    try:
        # Fetch a random image using Lexica API
        response = lexica_api.search_images(prompt="maid", limit=1)

        if response and response['images']:
            image_url = response['images'][0]['url']
            await message.reply_photo(image_url)
        else:
            await message.reply_text("No waifu found with the specified tags.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
