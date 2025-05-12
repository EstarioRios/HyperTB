import os
import json


def addProxy(hostName, port, secret):
    """
    Adds a new proxy configuration to a JSON file.

    Args:
        hostName (str): The hostname or IP address of the proxy
        port (int): The port number of the proxy
        secret (str): The secret/key for the proxy authentication
    """

    # Create a dictionary with the proxy data
    inputed_data = {"hostName": hostName, "port": port, "secret": secret}

    # Construct the full file path for proxies.json in the same directory as this script
    file_path = os.path.join(os.path.dirname(__file__), "proxies.json")

    # If the JSON file doesn't exist, create it with an empty list
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    # Read the existing data from the JSON file
    with open(file_path, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    # Add the new proxy data to the existing list
    loaded_data.append(inputed_data)

    # Write the updated data back to the JSON file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(loaded_data, f, ensure_ascii=False, indent=4)
        print("Proxy added.")


def subBotInfo(api_id, api_hash):
    """
    Saves bot API credentials to a JSON file.

    Args:
        api_id (int): Telegram API ID
        api_hash (str): Telegram API hash
    """
    file_path = os.path.join(os.path.dirname(__file__), "BotInfo.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            {"api_id": api_id, "api_hash": api_hash},
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
            print(f"API ID: {deserialized_data['api_id']}")
            print(f"API Hash: {deserialized_data['api_hash']}")

    except FileNotFoundError:
        print("Error: BotInfo.json file not found!")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in BotInfo.json!")


while True:
    # Print main menu header
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

        # Get Telegram API credentials from user
        api_id = input("Write the 'Api-ID': ")  # Telegram API ID (from my.telegram.org)
        api_hash = input(
            "Write the 'Api-Hash': "
        )  # Telegram API hash (from my.telegram.org)

        # Save the API credentials to file
        subBotInfo(api_id=api_id, api_hash=api_hash)

    # Option 3: View saved bot information
    elif q1 == "3":
        print("=================================================")

        # Display the saved bot credentials
        showBotInfo()

    # Note: Consider adding an exit option (e.g., elif q1 == "4": break)
    # to allow users to exit the infinite loop
