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

        # Print results
        print(f"🎬 Title: {title}")
        print(f"📦 Size (approx.): {filesize_mb} MB")
        print(f"📺 Available Resolutions: {available_resolutions}")

    except Exception as e:
        print(f"❌ Error: {e}")
