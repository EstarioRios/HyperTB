import os, re
import json
import sys
from telethon.errors import RPCError
import asyncio
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from YouTubeScript.YouTubeDownloader import get_youtube_info, download_youtube_video
from ..SoundCloudScript.MusicDownloader import download_soundcloud_track

# def proxy_finder():
#     """
#     Tests all proxies from proxies.json using Telethon with bot_token
#     and returns the first working one.
#
#     Returns:
#         tuple: (success_status: bool, proxy_config: dict or None)
#     """
#     # Path to proxies.json
#     proxies_path = os.path.join(os.path.dirname(__file__), "proxies.json")
#     if not os.path.exists(proxies_path):
#         print("Error: proxies.json file not found!")
#         return False, None
#
#     try:
#         with open(proxies_path, "r", encoding="utf-8") as f:
#             proxies = json.load(f)
#     except json.JSONDecodeError:
#         print("Error: Invalid JSON format in proxies.json!")
#         return False, None
#
#     if not proxies:
#         print("No proxies available in the file!")
#         return False, None
#
#     # Load bot token
#     botinfo_path = os.path.join(os.path.dirname(__file__), "BotInfo.json")
#     try:
#         with open(botinfo_path, "r", encoding="utf-8") as f:
#             bot_info = json.load(f)
#             bot_token = bot_info["bot_token"]
#     except Exception as e:
#         print(f"Error loading BotInfo.json: {str(e)}")
#         return False, None
#
#     print(f"Testing {len(proxies)} proxies...")
#
#     for proxy in proxies:
#         # MTProto proxy settings
#         proxy_config = (proxy["hostName"], int(proxy["port"]), proxy["secret"])
#
#         try:
#             # Create temporary client with proxy
#             client = TelegramClient(
#                 session=StringSession(),  # Use memory session
#                 api_id=0,  # Not used with bot_token
#                 api_hash="",  # Not used with bot_token
#                 proxy=("mtproxy", proxy_config[0], proxy_config[1], proxy_config[2]),
#             )
#
#             async def test_proxy():
#                 try:
#                     await client.start(bot_token=bot_token)
#                     me = await client.get_me()
#                     print(f"✅ Working proxy: {proxy['hostName']}:{proxy['port']}")
#                     print(f"   Connected as: {me.first_name} (@{me.username})")
#                     await client.disconnect()
#                     return True
#                 except RPCError as e:
#                     print(f"❌ RPC Error: {str(e)}")
#                 except Exception as e:
#                     print(f"⚠️ Error with {proxy['hostName']}: {str(e)}")
#                 return False
#
#             import asyncio
#
#             if asyncio.run(test_proxy()):
#                 return True, {
#                     "scheme": "mtproto",
#                     "hostname": proxy["hostName"],
#                     "port": int(proxy["port"]),
#                     "secret": proxy["secret"],
#                 }
#
#         except Exception as e:
#             print(f"❌ Failed to initialize client: {str(e)}")
#
#     print("No working proxies found!")
#     return False, None


# =========================================================================================================
# ================================Telegram Bot===============================================================
# =========================================================================================================


async def main():
    # Load bot credentials from BotInfo.json
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

    # Create Telegram client
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.start(bot_token=bot_token)

    # Define supported languages and language buttons
    languages = {
        "🇺🇸 English": "lang_en",
        "🇸🇦 Arabic": "lang_ar",
        "🇮🇷 Persian": "lang_fa",
        "🇷🇺 Russian": "lang_ru",
    }
    select_languages_buttons = [
        Button.inline(name, lang.encode()) for name, lang in languages.items()
    ]

    # Store user-selected languages
    user_language = {}

    # Load translated text based on selected language
    async def text_loader(event, text_key):
        try:
            with open(
                os.path.join(os.path.dirname(__file__), "languages.json"),
                mode="r",
                encoding="utf-8",
            ) as file:
                languages_file_data = json.load(file)
                lang_code = user_language.get(event.sender_id, "lang_en")
                for lang in languages_file_data:
                    if lang["language_form"] == lang_code:
                        return lang.get(text_key, f"⚠️ Missing key '{text_key}'")
                return f"⚠️ Language '{lang_code}' not found"
        except Exception as e:
            return f"⚠️ Error loading languages file: {str(e)}"

    # Handle /start command
    @client.on(events.NewMessage(pattern="/start"))
    async def start_handler(event):
        await event.respond(
            "👋 Welcome to HyperTB!\n\nWe're happy to see you here 😊\n🌐 Please choose your language to begin:",
            buttons=select_languages_buttons,
        )

    # Define service buttons
    services_buttons = [
        Button.inline("Download from YouTube", b"service_youtube_get_info"),
        Button.inline("Download from SoundCloud", b"service_soundcloud_download"),
    ]

    # Handle language selection
    async def language_selector(event, data):
        user_id = event.sender_id
        user_language[user_id] = data
        await event.respond(
            await text_loader(event, "language_choiced"), buttons=services_buttons
        )

    # Handle YouTube video info fetch
    async def youtube_get_info(event):
        await event.respond(await text_loader(event, "send_link"))
        link_event = await client.wait_event(
            events.NewMessage(func=lambda e: e.sender_id == event.sender_id)
        )
        link = link_event.raw_text.strip()

        error, title, filesize_mb, resolutions = await get_youtube_info(link)

        if not error:
            buttons = [
                Button.inline(
                    res, f"service_video_download_$^reso:{res}$^_link:{link}$^".encode()
                )
                for res in resolutions
            ]
            await event.respond(
                f"🎬 Title: {title}\n📦 Approx. Size (Best Quality): {filesize_mb} MB\n📺 Available Resolutions:",
                buttons=buttons,
            )
        else:
            await event.respond(f"{await text_loader(event, 'bad_request')}\n{error}")

    # Handle YouTube video download
    async def youtube_download(event, link, resolution):
        try:
            await event.respond(await text_loader(event, "download_started"))
            video_path = await download_youtube_video(link, resolution)
            await event.respond(await text_loader(event, "video_downloaded"))
            await event.respond(
                message=await text_loader(event, "your_video_is_here"), file=video_path
            )
            if os.path.exists(video_path):
                os.remove(video_path)
        except:
            await event.respond(await text_loader(event, "bad_request"))

    # Handle SoundCloud track download
    async def soundcloud_download(event):
        await event.respond(await text_loader(event, "send_link"))
        link_event = await client.wait_event(
            events.NewMessage(func=lambda e: e.sender_id == event.sender_id)
        )
        link = link_event.raw_text.strip()

        error, file_path = await download_soundcloud_track(url=link)

        if not error:
            await event.respond(
                await text_loader(event, "music_downloaded"), file=file_path
            )
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            await event.respond(await text_loader(event, "bad_request"))

    # Handle all callback queries (inline button presses)
    @client.on(events.CallbackQuery)
    async def callback_handler(event):
        data = event.data.decode()

        if data.startswith("lang_"):
            await language_selector(event, data)

        elif data == "service_youtube_get_info":
            await youtube_get_info(event)

        elif data.startswith("service_video_download_"):
            match = re.search(r"reso:(.*?)\$\^_link:(.*?)\$\^", data)
            if match:
                reso = match.group(1)
                link = match.group(2)
                await youtube_download(event, link, reso)
            else:
                await event.respond(await text_loader(event, "bad_request"))

        elif data == "service_soundcloud_download":
            await soundcloud_download(event)

        else:
            await event.respond(await text_loader(event, "bad_request"))

    print("✅ Bot is running...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
