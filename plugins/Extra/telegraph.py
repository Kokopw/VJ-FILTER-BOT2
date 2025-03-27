import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

CATBOX_API = "https://catbox.moe/user/api.php"

# Step 1: Ask for media when using /telegraph
@Client.on_message(filters.command("telegraph") & filters.private)
async def ask_for_media(client, message: Message):
    await message.reply_text("📸 **Send me your image, video, or audio file (max 200MB)** to upload on Catbox.")


# Step 2: Handle media upload
@Client.on_message(filters.media & filters.private)
async def c_upload(client, message: Message):
    uploading_msg = await message.reply_text("<b>ᴜᴘʟᴏᴀᴅɪɴɢ...</b>")

    try:
        # Download media
        downloaded_media = await message.download()

        if not downloaded_media:
            return await uploading_msg.edit_text("**Failed to download media. Try again!**")

        # Uploading to Catbox
        with open(downloaded_media, "rb") as f:
            response = requests.post(CATBOX_API, data={"reqtype": "fileupload"}, files={"fileToUpload": f})

        if response.status_code == 200:
            file_url = response.text.strip()

            # Buttons layout
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Open Link", url=file_url),
                 InlineKeyboardButton(text="Share Link", url=f"https://telegram.me/share/url?url={file_url}")],
                [InlineKeyboardButton(text="✗ Close ✗", callback_data="close")]
            ])

            # Send result with buttons
            await uploading_msg.edit_text(
                text=f"<b>Link :-</b>\n\n<code>{file_url}</code>",
                disable_web_page_preview=True,
                reply_markup=buttons
            )

        else:
            await uploading_msg.edit_text("**Upload failed. Try again later!**")

        # Clean up
        os.remove(downloaded_media)

    except Exception as e:
        await uploading_msg.edit_text(f"**Error:** `{str(e)}`")


# Step 3: Handle Close Button
@Client.on_callback_query(filters.regex("close"))
async def close_callback(client, callback_query: CallbackQuery):
    await callback_query.message.delete()
