import os
import yt_dlp
import glob


# Asynchronously download a SoundCloud track as an MP3
async def download_soundcloud_track(url: str):
    download_dir = "../Downloads"  # Directory to save downloaded files
    os.makedirs(download_dir, exist_ok=True)  # Create directory if it doesn't exist

    # Configuration options for yt_dlp
    ydl_opts = {
        "format": "bestaudio/best",  # Download best available audio format
        "outtmpl": os.path.join(
            download_dir, "%(title)s.%(ext)s"
        ),  # Output file naming pattern
        "postprocessors": [  # Convert audio to MP3 after download
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,  # Suppress console output
        "no_warnings": True,  # Suppress warnings
    }

    try:
        # Start the download process
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Find the most recently created MP3 file in the download directory
        files = glob.glob(os.path.join(download_dir, "*.mp3"))
        if not files:
            return "File not found after download", None

        latest_file = max(files, key=os.path.getctime)  # Get the newest file
        return None, latest_file  # Return (error_message, file_path)

    except Exception as e:
        return str(e), None  # Return the error message if something went wrong
