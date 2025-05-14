import os
import json
from telethon.errors import RPCError
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession


def proxy_finder():
    """
    Tests all proxies from proxies.json using Telethon with bot_token
    and returns the first working one.

    Returns:
        tuple: (success_status: bool, proxy_config: dict or None)
    """
    # Path to proxies.json
    proxies_path = os.path.join(os.path.dirname(__file__), "proxies.json")
    if not os.path.exists(proxies_path):
        print("Error: proxies.json file not found!")
        return False, None

    try:
        with open(proxies_path, "r", encoding="utf-8") as f:
            proxies = json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in proxies.json!")
        return False, None

    if not proxies:
        print("No proxies available in the file!")
        return False, None

    # Load bot token
    botinfo_path = os.path.join(os.path.dirname(__file__), "BotInfo.json")
    try:
        with open(botinfo_path, "r", encoding="utf-8") as f:
            bot_info = json.load(f)
            bot_token = bot_info["bot_token"]
    except Exception as e:
        print(f"Error loading BotInfo.json: {str(e)}")
        return False, None

    print(f"Testing {len(proxies)} proxies...")

    for proxy in proxies:
        # MTProto proxy settings
        proxy_config = (proxy["hostName"], int(proxy["port"]), proxy["secret"])

        try:
            # Create temporary client with proxy
            client = TelegramClient(
                session=StringSession(),  # Use memory session
                api_id=0,  # Not used with bot_token
                api_hash="",  # Not used with bot_token
                proxy=("mtproxy", proxy_config[0], proxy_config[1], proxy_config[2]),
            )

            async def test_proxy():
                try:
                    await client.start(bot_token=bot_token)
                    me = await client.get_me()
                    print(f"✅ Working proxy: {proxy['hostName']}:{proxy['port']}")
                    print(f"   Connected as: {me.first_name} (@{me.username})")
                    await client.disconnect()
                    return True
                except RPCError as e:
                    print(f"❌ RPC Error: {str(e)}")
                except Exception as e:
                    print(f"⚠️ Error with {proxy['hostName']}: {str(e)}")
                return False

            import asyncio

            if asyncio.run(test_proxy()):
                return True, {
                    "scheme": "mtproto",
                    "hostname": proxy["hostName"],
                    "port": int(proxy["port"]),
                    "secret": proxy["secret"],
                }

        except Exception as e:
            print(f"❌ Failed to initialize client: {str(e)}")

    print("No working proxies found!")
    return False, None


# =========================================================================================================
# ================================elegram Bot===============================================================
# =========================================================================================================


async def main():
    # Step 1: Find working proxy
    proxy_status, proxy_config = proxy_finder()

    if not proxy_status:
        print("Cannot start bot - no working proxy available!")
        return

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
        proxy=(
            "mtproxy",
            proxy_config["hostname"],
            proxy_config["port"],
            proxy_config["secret"],
        ),
    )

    # Step 4: Start bot
    await client.start(bot_token=bot_token)

    # Handle /start command
    @client.on(events.NewMessage(pattern="/start"))
    async def handler_start(event):
        await event.respond("Hello! I'm a simple echo bot.")

    # Handle any text message in private chat
    @client.on(events.NewMessage())
    async def handler_echo(event):
        if event.is_private and event.message.text != "/start":
            await event.respond(f"You said: {event.message.text}")

    print("✅ Bot is running with proxy...")
    await client.run_until_disconnected()


# Entry point
if __name__ == "__main__":
    asyncio.run(main())
