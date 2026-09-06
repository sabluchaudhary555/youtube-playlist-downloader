#!/usr/bin/env python3
"""
YouTube Playlist Downloader
----------------------------
Downloads all videos from a YouTube playlist using yt-dlp.

Requirements:
    pip install -r requirements.txt

Usage:
    python yt_playlist_downloader.py
    (then paste the playlist URL when prompted)

    OR run directly with a URL:
    python yt_playlist_downloader.py "https://www.youtube.com/playlist?list=XXXXXXXX"
"""

import sys
import os

try:
    import yt_dlp
except ImportError:
    print("yt-dlp is not installed. Install it first with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)


def download_playlist(playlist_url: str, output_dir: str = "downloads", audio_only: bool = False):
    
    os.makedirs(output_dir, exist_ok=True)

    # Output filename template: "01 - Video Title.ext" inside a playlist-named folder
    outtmpl = os.path.join(output_dir, "%(playlist_title)s", "%(playlist_index)02d - %(title)s.%(ext)s")

   
    # NOTE: this file is created inside `output_dir` (the base "downloads"
    # folder), NOT inside the playlist's own subfolder. Keep that in mind
    # when using revalidate_downloads.py later.
    archive_path = os.path.join(output_dir, "downloaded_archive.txt")

    ydl_opts = {
        "outtmpl": outtmpl,
        "ignoreerrors": True,       # skip unavailable/private videos instead of stopping
        "noplaylist": False,        # ensure playlist mode is respected
        "concurrent_fragment_downloads": 4,
        "progress_hooks": [progress_hook],
        "download_archive": archive_path,   # <-- enables resume support
        "continuedl": True,                 # resume a partially-downloaded file too
    }

    if audio_only:
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        ydl_opts.update({
            # Try best quality up to 720p first; if that's not available
            # for a given video, fall back to the lowest quality offered.
            "format": "bestvideo[height<=720]+bestaudio/best[height<=720]/worst",
            "merge_output_format": "mp4",
        })

    print(f"\nStarting download for playlist:\n  {playlist_url}\n")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

    print("\nAll done. Check the 'downloads' folder for your videos.")


def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        filename = os.path.basename(d.get("filename", ""))
        print(f"\r  Downloading: {filename[:50]:<50} {percent:>7} {speed}", end="", flush=True)
    elif d["status"] == "finished":
        print(f"\n  Finished: {os.path.basename(d.get('filename', ''))}")


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter the YouTube playlist URL: ").strip()

    if not url:
        print("No URL provided. Exiting.")
        sys.exit(1)

    audio_choice = input("Download audio only (mp3)? [y/N]: ").strip().lower()
    audio_only = audio_choice == "y"

    download_playlist(url, audio_only=audio_only)
    # Note: video quality is fixed at "720p, or lowest available if 720p
    # isn't offered" — see download_playlist()'s format selector.


if __name__ == "__main__":
    main()