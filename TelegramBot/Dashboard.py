import os, re
import json
import sys
from telethon.errors import RPCError
import asyncio
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from YouTubeScript.YouTubeDownloader import get_youtube_info, download_youtube_video
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


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
    # # Step 1: Find working proxy
    # proxy_status, proxy_config = proxy_finder()

    # if not proxy_status:
    #     print("Cannot start bot - no working proxy available!")
    #     return

    # Step 2: Load bot_token from BotInfo.json
    bot_info_path = os.path.join(os.path.dirname(__file__), "BotInfo.json")
    try:
        with open(bot_info_path, "r", encoding="utf-8") as f:
            deserialized_data = json.load(f)
            bot_token = deserialized_data["bot_token"]
    except Exception as e:
        print(f"Error loading bot token: {str(e)}")
        return

    # Step 3: Create TelegramClient with MTProto proxy and bot_token
    client = TelegramClient(
        session=StringSession(),
        api_id=0,
        api_hash="",
        # proxy=(
        #     "mtproxy",
        #     proxy_config["hostname"],
        #     proxy_config["port"],
        #     proxy_config["secret"],
        # ),
    ).start(bot_token=bot_token)

    languages = {
        "🇺🇸 English": "lang_en",
        "🇸🇦 Arabic": "lang_ar",
        "🇮🇷 Persian": "lang_fa",
        "🇷🇺 Russian": "lang_ru",
    }

    select_langauges_buttons = [
        Button.inline(name, lan.encode()) for name, lan in languages.items()
    ]

    user_language = {}

    async def text_loader(event, text_key):
        languages_file_path = os.path.join(os.path.dirname(__file__), "languages.json")
        try:
            with open(languages_file_path, mode="r", encoding="utf-8") as file:
                languages_file_data = json.load(file)
                lang_code = user_language.get(event.sender_id, "lang_en")
                for language in languages_file_data:
                    if language["language_form"] == lang_code:
                        return language.get(text_key, f"⚠️ Missing key '{text_key}'")
            return f"⚠️ Language '{lang_code}' not found"
        except Exception as e:
            return f"⚠️ Error loading languages file: {str(e)}"

    # Handle /start command
    @client.on(events.NewMessage)
    async def handler_start(event):
        recived_message = event.raw_text.strip()

        # user_language = {event.sender_id: "lang_en"}

        if recived_message == "/start":
            await event.respond(
                "👋 Welcome to HyperTB!\n\n"
                "We're happy to see you here 😊\n"
                "🌐 Please choose your language to begin:",
                buttons=select_langauges_buttons,
            )

    services_buttons = [
        Button.inline("Download from YouTube", "service_youtube_get_info"),
        Button.inline("Download from SoundCloud", "service_soundcloud_download"),
    ]

    async def language_selector(event, data):
        user_id = event.data.sender_id
        user_language[user_id] = data
        await event.respond(
            await text_loader(event, "language_choiced"), buttons=services_buttons
        )

    async def youtube_get_info(event):
        await event.respond(await text_loader(event, "send_link"))

        response = await client.wait_event(
            events.NewMessage(func=lambda e: e.sender_id == event.sender_id)
        )

        link = response.raw_text.strip()

        error, title, filesize_mb, available_resolutions = await get_youtube_info(link)

        if not error:

            resolutions_buttons = [
                (
                    Button.inline(
                        str(res),
                        f"service_video_download_$^reso:{str(available_resolutions)}$^_link:{link}$^",
                    )
                )
                for res in available_resolutions
            ]
            await event.respond(
                f"🎬 Title: {title}\n"
                f"📦 Approx. Size (Best Quality): {filesize_mb} MB\n"
                f"📺 Available Resolutions:",
                buttons=resolutions_buttons,
            )
        else:
            await event.respond(
                f"{await text_loader(event, 'bad_request')}\n{str(error)} ||| This message is not deppent on language"
            )

    async def youtube_download(event, link, resolution):
        try:
            await event.respond(await text_loader(event, "download_started"))
            downloaded_video_path = await download_youtube_video(link, resolution)
            await event.respond(await text_loader(event, "video_downloaded"))
            await event.respond(
                message=await text_loader(event, "your_video_is_here"),
                file=downloaded_video_path,
            )
            if os.path.exists(downloaded_video_path):
                os.remove(downloaded_video_path)

        except:
            await event.respond(await text_loader(event, "bad_request"))







    async def soundcloud_download(event, link):
        pass









    @client.on(events.CallbackQuery)
    async def callback_dispatcher(event):
        data = event.data.decode()
        data = str(data)

        if data.startswith("lang_"):
            await language_selector(event, data)
        elif data.startswith("service_"):
            if data == "service_youtube_get_info":
                await youtube_get_info(event)
            if data.startswith("service_video_download_"):
                data = str(data)
                match = re.search(r"reso:(.*?)\$\^_link:(.*?)\$\^", data)
                if match:

                    video_target_resolution = match.group(1)
                    video_link = match.group(2)
                    await youtube_download(event, video_link, video_target_resolution)

                else:
                    await event.respond(await text_loader(event, "bad_request"))
            if data == "service_soundcloud_download":
                pass

        else:
            await event.respond(await text_loader(event, "bad_request"))

    @client.on(events.NewMessage())
    async def handler_echo(event):
        if event.is_private and event.message.text != "/start":
            await event.respond(f"You said: {event.message.text}")

    # print("✅ Bot is running with proxy...")
    print("✅ Bot is running...")
    await client.run_until_disconnected()


# Entry point
if __name__ == "__main__":
    asyncio.run(main())
