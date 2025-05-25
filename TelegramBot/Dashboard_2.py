import os
import re
import json
import sys
import asyncio

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from YouTubeScript.YouTubeDownloader import get_youtube_info, download_youtube_video


async def main():
    # Step 2: Load bot_token from BotInfo.json
    bot_info_path = os.path.join(os.path.dirname(__file__), "BotInfo.json")
    try:
        with open(bot_info_path, "r", encoding="utf-8") as f:
            deserialized_data = json.load(f)
            bot_token = deserialized_data["token"]
            api_id = deserialized_data["api_id"]
            api_hash = deserialized_data["api_hash"]
    except Exception as e:
        print(f"Error loading bot token: {str(e)}")
        return

    # Create Pyrogram Client (bot)
    app = Client(
        "hyperbot",
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token,
        # proxy=None  # اگر پروکسی دارید اینجا قرار دهید
    )

    languages = {
        "🇺🇸 English": "lang_en",
        "🇸🇦 Arabic": "lang_ar",
        "🇮🇷 Persian": "lang_fa",
        "🇷🇺 Russian": "lang_ru",
    }

    select_languages_buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(name, callback_data=lan)]
            for name, lan in languages.items()
        ]
    )

    user_language = {}

    async def text_loader(user_id, text_key):
        languages_file_path = os.path.join(os.path.dirname(__file__), "languages.json")
        try:
            with open(languages_file_path, mode="r", encoding="utf-8") as file:
                languages_file_data = json.load(file)
                lang_code = user_language.get(user_id, "lang_en")
                for language in languages_file_data:
                    if language["language_form"] == lang_code:
                        return language.get(text_key, f"⚠️ Missing key '{text_key}'")
            return f"⚠️ Language '{lang_code}' not found"
        except Exception as e:
            return f"⚠️ Error loading languages file: {str(e)}"

    @app.on_message(filters.command("start"))
    async def handler_start(client, message):
        await message.reply(
            "👋 Welcome to HyperTB!\n\n"
            "We're happy to see you here 😊\n"
            "🌐 Please choose your language to begin:",
            reply_markup=select_languages_buttons,
        )

    services_buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Download from YouTube", callback_data="service_youtube_get_info"
                )
            ],
            [
                InlineKeyboardButton(
                    "Download from SoundCloud",
                    callback_data="service_soundcloud_download",
                )
            ],
        ]
    )

    async def language_selector(client, callback_query: CallbackQuery, data: str):
        user_id = callback_query.from_user.id
        user_language[user_id] = data
        await callback_query.answer()
        await callback_query.message.edit_text(
            await text_loader(user_id, "language_choiced"),
            reply_markup=services_buttons,
        )

    async def youtube_get_info(client, callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        await callback_query.answer()
        await callback_query.message.edit_text(await text_loader(user_id, "send_link"))

        # Wait for next message from same user
        @app.on_message(filters.user(user_id) & filters.private)
        async def get_link(client, message):
            link = message.text.strip()
            error, title, filesize_mb, available_resolutions = await get_youtube_info(
                link
            )

            if not error:
                resolutions_buttons = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                str(res),
                                callback_data=f"service_video_download_$^reso:{str(available_resolutions)}$^_link:{link}$^",
                            )
                        ]
                        for res in available_resolutions
                    ]
                )
                await message.reply(
                    f"🎬 Title: {title}\n"
                    f"📦 Approx. Size (Best Quality): {filesize_mb} MB\n"
                    f"📺 Available Resolutions:",
                    reply_markup=resolutions_buttons,
                )
            else:
                await message.reply(
                    f"{await text_loader(user_id, 'bad_request')}\n{str(error)} ||| This message is not dependent on language"
                )
            # Remove handler after use
            app.remove_handler(get_link)

    async def youtube_download(
        client, callback_query: CallbackQuery, link: str, resolution: str
    ):
        user_id = callback_query.from_user.id
        await callback_query.answer()
        try:
            await callback_query.message.edit(
                await text_loader(user_id, "download_started")
            )
            downloaded_video_path = await download_youtube_video(link, resolution)
            await callback_query.message.reply(
                await text_loader(user_id, "video_downloaded")
            )
            await callback_query.message.reply(
                await text_loader(user_id, "your_video_is_here"),
                reply_markup=None,
                # در Pyrogram برای ارسال فایل به صورت reply باید پیام جداگانه بفرستیم:
                # callback_query.message.reply_video(downloaded_video_path) اما چون async هستیم از send_video استفاده می‌کنیم
            )
            await client.send_video(user_id, downloaded_video_path)

            if os.path.exists(downloaded_video_path):
                os.remove(downloaded_video_path)

        except Exception:
            await callback_query.message.reply(
                await text_loader(user_id, "bad_request")
            )

    async def soundcloud_download(client, callback_query: CallbackQuery):
        # Placeholder for SoundCloud download functionality
        await callback_query.answer()
        await callback_query.message.edit_text(
            "SoundCloud download feature is under development."
        )

    @app.on_callback_query()
    async def callback_dispatcher(client, callback_query: CallbackQuery):
        data = (
            callback_query.data.decode()
            if isinstance(callback_query.data, bytes)
            else callback_query.data
        )
        if data.startswith("lang_"):
            await language_selector(client, callback_query, data)
        elif data.startswith("service_"):
            if data == "service_youtube_get_info":
                await youtube_get_info(client, callback_query)
            elif data.startswith("service_video_download_"):
                match = re.search(r"reso:(.*?)\$\^_link:(.*?)\$\^", data)
                if match:
                    video_target_resolution = match.group(1)
                    video_link = match.group(2)
                    await youtube_download(
                        client, callback_query, video_link, video_target_resolution
                    )
                else:
                    await callback_query.answer("Bad request", show_alert=True)
            elif data == "service_soundcloud_download":
                await soundcloud_download(client, callback_query)
        else:
            await callback_query.answer("Bad request", show_alert=True)

    @app.on_message(filters.private & ~filters.command("start"))
    async def handler_echo(client, message):
        await message.reply(f"You said: {message.text}")

    print("✅ Bot is running...")
    await app.start()
    await app.idle()


if __name__ == "__main__":
    asyncio.run(main())
