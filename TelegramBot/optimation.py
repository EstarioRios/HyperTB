# optimation.py

import os
import json

# Define the maximum download size limit in MB
MAX_FOLDER_SIZE_MB = 700


def smart_download(down_link, size_mb, user_id, resolution, file_type):
    """
    Manages download scheduling based on folder size limit.
    If adding the new download exceeds the max limit, it queues the download.
    Otherwise, it allows it to proceed.

    Args:
        down_link (str): Direct download link
        size_mb (float): Size of the file to be downloaded in MB
        user_id (int): Telegram user ID of the requester
        resolution (str): Selected resolution (for videos)

    Returns:
        dict: Information about whether the download should start or be queued
    """

    # Construct path to the JSON file that stores all download entries
    download_list_file_path = os.path.abspath(
        os.path.join("Download", "download_list.json")
    )

    # Ensure the file exists; if not, create it with an empty list
    if not os.path.exists(download_list_file_path):
        with open(download_list_file_path, mode="w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)

    # Load current download list
    with open(download_list_file_path, mode="r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = []

    # Calculate total ongoing download size
    current_total_size = sum(float(item["size_mb"]) for item in data)

    # If adding this download won't exceed limit, allow it to start
    if current_total_size + float(size_mb) <= MAX_FOLDER_SIZE_MB:
        dp_number = max([item["dp_number"] for item in data], default=0) + 1

        data.append(
            {
                "type": str(file_type),
                "link": down_link,
                "size_mb": size_mb,
                "user_id": user_id,
                "resolution": resolution,
                "dp_number": dp_number,
            }
        )

        with open(download_list_file_path, mode="w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return True

    # Otherwise, queue the download
    else:
        later_download_list_file_path = os.path.abspath(
            os.path.join("Download", "download_later_list.json")
        )

        if not os.path.exists(later_download_list_file_path):
            with open(
                later_download_list_file_path, mode="w", encoding="utf-8"
            ) as file:
                data = []
                json.dump(data, ensure_ascii=False, indent=4)
        else:
            with open(
                later_download_list_file_path, mode="r", encoding="utf-8"
            ) as file:
                data = json.load(file)

        queue_entry = {
            "type": str(file_type),
            "link": down_link,
            "size_mb": size_mb,
            "user_id": user_id,
            "resolution": resolution,
            "dp_number": max([item["dp_number"] for item in data], default=0) + 1,
        }

        data.append(queue_entry)

        with open(download_list_file_path, mode="w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return False
