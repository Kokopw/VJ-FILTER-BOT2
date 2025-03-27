import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

CATBOX_API = "https://catbox.moe/user/api.php"

@Client.on_message(filters.command("telegraph") & filters.reply)
async def c_upload(client, message: Message):
    reply = message.reply_to_message

    if not reply.media:
        return await message.reply_text("**Reply to an image, video, or audio file (max 200MB) to upload to Catbox.**")

    if reply.document and reply.document.file_size > 200 * 1024 * 1024:
        return await message.reply_text("**File size limit is 200MB for Catbox.**")

    uploading_msg = await message.reply_text("<b>ᴜᴘʟᴏᴀᴅɪɴɢ...</b>")

    try:
        # Download media
        downloaded_media = await reply.download()
        
        if not downloaded_media:
            return await uploading_msg.edit_text("**Failed to download media. Try again!**")

        # Uploading to Catbox
        with open(downloaded_media, "rb") as f:
            response = requests.post(CATBOX_API, data={"reqtype": "fileupload"}, files={"fileToUpload": f})

        if response.status_code == 200:
            file_url = response.text.strip()

            # Same button layout as old code
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
