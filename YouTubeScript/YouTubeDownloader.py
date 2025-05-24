import os
from pytube import YouTube
from pytube import YouTube


async def get_youtube_info(url):
    try:
        # Create a YouTube object
        yt = YouTube(url)

        # Get video title
        title = yt.title

        # Get all progressive mp4 streams (video + audio)
        streams = (
            yt.streams.filter(progressive=True, file_extension="mp4")
            .order_by("resolution")
            .desc()
        )

        if not streams:
            error = "⚠️ No downloadable streams found."

        # Get the highest resolution stream to calculate approximate size
        best_stream = streams[0]
        filesize_bytes = best_stream.filesize or 0
        filesize_mb = round(filesize_bytes / 1024 / 1024, 2)

        # List of available resolutions
        available_resolutions = [stream.resolution for stream in streams]
        error = None

        return error, title, filesize_mb, available_resolutions
    except Exception as e:

        error = f"❌ Error: {e}"
        title, filesize_mb, available_resolutions = None
        return error, title, filesize_mb, available_resolutions


async def download_youtube_video(link, resolution):
    try:
        # Create target download directory: one level above current → /Download/
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        download_dir = os.path.join(parent_dir, "Download")
        os.makedirs(download_dir, exist_ok=True)  # Create folder if not exists

        # Load video
        yt = YouTube(link)

        # Filter streams by desired resolution and file format (usually mp4)
        stream = yt.streams.filter(
            progressive=True, file_extension="mp4", res=resolution
        ).first()

        if stream is None:
            raise ValueError(
                f"No video found at {resolution} resolution for this link."
            )

        # Download video to the download directory
        downloaded_path = stream.download(output_path=download_dir)

        # Return absolute path using os
        downloaded_video_path = os.path.abspath(downloaded_path)
        return downloaded_video_path

    except Exception as e:
        return None
