# optimation.py

import os
import json
from YouTubeScript.YouTubeDownloader import download_youtube_video
from SoundCloudScript.MusicDownloader import download_soundcloud_track

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


async def donwload_status_checker():
    download_list_path = os.path.abspath(os.path.join("Download", "download_list.json"))
    download_later_list_path = os.path.abspath(
        os.path.join("Download", "download_later_list.json")
    )

    if not os.path.exists(download_list_path):
        with open(download_list_path, mode="w", encoding="utf-8") as file:
            now_down_data = []
            json.dump(now_down_data)

    with open(download_list_path, mode="r", encoding="utf-8") as file:
        now_down_data = json.load(fp=file)

    if (not now_down_data) or (now_down_data == []):

        if not os.path.exists(download_later_list_path):

            with open(download_later_list_path, "w", encoding="utf-8") as file:
                later_down_data = []
                json.dump(later_down_data)
        else:
            with open(download_later_list_path, mode="r", encoding="utf-8") as file:
                later_down_data = json.load(file)

                if later_down_data == []:
                    pass
                else:
                    for e in later_down_data:
                        file_type = e["type"]
                        file_link = e["link"]
                        file_resolution = e["resolution"]
                        user_id = e["user_id"]

                        if file_type == "video":

                            await download_youtube_video(
                                link=file_link,
                                resolution=file_resolution,
                                user_id=user_id,
                            )
                        if file_type == "music":
                            await download_soundcloud_track(url=file_link)
