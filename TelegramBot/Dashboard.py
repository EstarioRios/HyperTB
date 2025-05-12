import os
import json
from pyrogram import Client, filters
from pyrogram.errors import ConnectionError


def proxy_finder():
    """
    Tests all proxies from proxies.json and returns the first working one.

    Returns:
        tuple: (success_status: bool, proxy_config: dict or None)
    """
    # Load proxies list
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

    # Load Telegram API credentials
    botinfo_path = os.path.join(os.path.dirname(__file__), "BotInfo.json")
    try:
        with open(botinfo_path, "r", encoding="utf-8") as f:
            bot_info = json.load(f)
            api_id = bot_info["api_id"]
            api_hash = bot_info["api_hash"]
    except Exception as e:
        print(f"Error loading BotInfo.json: {str(e)}")
        return False, None

    print(f"Testing {len(proxies)} proxies...")

    for proxy in proxies:
        # Configure MTProto proxy
        proxy_config = {
            "scheme": "mtproto",
            "hostname": proxy["hostName"],
            "port": int(proxy["port"]),  # Convert port to integer
            "secret": proxy["secret"],  # MTProto secret key
        }

        # Create test client
        test_client = Client(
            "proxy_tester",  # Temporary session name
            api_id=api_id,
            api_hash=api_hash,
            proxy=proxy_config,
            no_updates=True,  # Disable updates for testing
        )

        try:
            # Test connection
            with test_client:
                user = test_client.get_me()
                print(f"✅ Working proxy: {proxy['hostName']}:{proxy['port']}")
                print(f"   Connected as: {user.first_name} (@{user.username})")
                return True, proxy_config

        except ConnectionError:
            print(f"❌ Connection failed: {proxy['hostName']}:{proxy['port']}")
        except Exception as e:
            print(f"⚠️ Error with {proxy['hostName']}: {str(e)}")

    print("No working proxies found!")
    return False, None


# =========================================================================================================
# ================================elegram Bot===============================================================
# =========================================================================================================

# First find a working proxy
proxy_status, proxy_config = proxy_finder()  # Using our previous function

if not proxy_status:
    print("Cannot start bot - no working proxy available!")
    exit()

# Basic echo bot that replies to messages
bot = Client(
    "my_bot",
    api_id=123456,  # Replace with your API ID
    api_hash="your_api_hash_here",  # Replace with your API hash
    proxy=proxy_config,  # Using our tested proxy
    plugins=dict(root="plugins"),  # Optional plugins directory
)


# Handler for text messages
@bot.on_message(filters.text & filters.private)
async def echo(client, message):
    await message.reply(f"You said: {message.text}")


# Handler for /start command
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Hello! I'm a simple echo bot.")


print("Bot is running...")
bot.run()
