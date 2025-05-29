# YouTubeDownloader.py

import os
from pytube import YouTube
from ..TelegramBot.optimation import smart_download


async def get_youtube_info(url):
    """
    Retrieves basic information about a YouTube video including:
    - Title
    - Approximate size (MB)
    - Available resolutions
    """
    try:
        # Create a YouTube object from URL
        yt = YouTube(url)

        # Get video title
        title = yt.title

        # Get progressive (video+audio) mp4 streams and sort by resolution descending
        streams = (
            yt.streams.filter(progressive=True, file_extension="mp4")
            .order_by("resolution")
            .desc()
        )

        if not streams:
            return "not_found", None, None, None

        # Get the top stream for size estimation
        best_stream = streams[0]
        filesize_bytes = best_stream.filesize or 0
        filesize_mb = round(filesize_bytes / 1024 / 1024, 2)

        # Extract available resolution list
        available_resolutions = [stream.resolution for stream in streams]

        return None, title, filesize_mb, available_resolutions

    except Exception as e:
        return f"❌ Error: {e}", None, None, None


async def download_youtube_video(link, resolution, user_id):
    """
    Downloads a YouTube video in the specified resolution,
    but only if the total folder size permits.
    Otherwise, queues the download request.

    Args:
        link (str): YouTube video URL
        resolution (str): Desired resolution (e.g., '720p')
        user_id (int): Telegram user ID of the requester

    Returns:
        tuple: (status, message, downloaded_path or None)
    """
    try:
        # Create YouTube object
        yt = YouTube(link)

        # Get the stream that matches the desired resolution
        stream = yt.streams.filter(
            progressive=True, file_extension="mp4", res=resolution
        ).first()

        if stream is None:
            return "error", f"No video found at {resolution} resolution.", None

        # Estimate video size
        file_size_mb = round((stream.filesize or 0) / 1024 / 1024, 2)

        # Call the smart_download function to decide whether to download now or later
        decision = smart_download(
            down_link=link,
            size_mb=file_size_mb,
            user_id=user_id,
            resolution=resolution,
            file_type="video",
        )

        if decision == False:
            # Video added to queue; no download now
            return "wait_to_download", None
        else:

            # Create download directory: /Download
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            download_dir = os.path.join(parent_dir, "Download")
            os.makedirs(download_dir, exist_ok=True)

            # Download the video file
            downloaded_path = stream.download(output_path=download_dir)
            absolute_path = os.path.abspath(downloaded_path)

            return None, absolute_path

    except Exception as e:
        return "error", None
