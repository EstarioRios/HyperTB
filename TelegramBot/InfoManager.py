import os
import json


def addProxy(hostName, port, secret):
    """
    Safely adds a new proxy configuration to proxies.json with full error handling.

    Args:
        hostName (str): Proxy hostname/IP
        port (int/str): Proxy port number
        secret (str): Proxy secret key

    Returns:
        bool: True if successful, False if failed
    """
    try:
        # Validate input parameters
        if not all([hostName, port, secret]):
            raise ValueError("All proxy parameters are required")

        # Convert port to integer
        try:
            port = int(port)
        except ValueError:
            raise ValueError("Port must be a valid number")

        # Prepare proxy data
        proxy_data = {
            "hostName": hostName.strip(),
            "port": port,
            "secret": secret.strip(),
        }

        # Determine file path
        file_path = os.path.join(os.path.dirname(__file__), "proxies.json")

        # Initialize empty list if file doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
                current_data = []
        else:
            # Safely read existing data (handles empty/corrupt files)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    current_data = json.load(f)
                    if not isinstance(current_data, list):
                        current_data = []  # Reset if not a list
            except (json.JSONDecodeError, ValueError):
                current_data = []  # Reset if corrupted

        # Add new proxy
        current_data.append(proxy_data)

        # Write back to file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(current_data, f, ensure_ascii=False, indent=4)

        print(f"✅ Proxy {hostName}:{port} added successfully.")
        return True

    except Exception as e:
        print(f"❌ Failed to add proxy: {str(e)}")
        return False


def subBotInfo(token):
    """
    Saves bot API credentials to a JSON file.

    Args:
        api_id (int): Telegram API ID
        api_hash (str): Telegram API hash
    """
    file_path = os.path.join(os.path.dirname(__file__), "BotInfo.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            {"token": token},
            f,  # You were missing the file object here
            ensure_ascii=False,
            indent=4,
        )
    # No need to assign json.dump to serialized_data - it returns None


def showBotInfo():
    """
    Reads and displays bot API credentials from the JSON file.
    """
    file_path = os.path.join(os.path.dirname(__file__), "BotInfo.json")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            deserialized_data = json.load(f)
            print("Bot Information:")
            print(f"Bot Token: {deserialized_data["token"]}")

    except FileNotFoundError:
        print("Error: BotInfo.json file not found!")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in BotInfo.json!")


while True:
    # Print main menu header
    print("=================================================")
    print("Hello wich of these do you wannt do?")

    # Get user choice for operation
    q1 = input("Add Proxy-1 / Submit Bot Information-2 / See Bot Information-3 (1/2/3)")

    # Option 1: Add new proxy configuration
    if q1 == "1":
        print("=================================================")

        # Get proxy details from user
        hostName = input("Write the 'HostName': ")  # Proxy hostname or IP address
        port = input("Write the 'Port': ")  # Proxy port number
        secret = input("Write the 'Secret': ")  # Proxy authentication secret

        # Validate that all required fields are provided
        if not all([hostName, port, secret]):  # Check if any field is empty
            print("Informations are requirement")  # Show error if any field missing
        else:
            # If validation passes, add the new proxy
            addProxy(hostName=hostName, port=port, secret=secret)

    # Option 2: Submit bot API credentials
    elif q1 == "2":
        print("=================================================")

        token = input("Write the 'Bot Token: '")

        # Save the API credentials to file
        subBotInfo(token=token)

    # Option 3: View saved bot information
    elif q1 == "3":
        print("=================================================")

        # Display the saved bot credentials
        showBotInfo()

    # Note: Consider adding an exit option (e.g., elif q1 == "4": break)
    # to allow users to exit the infinite loop
