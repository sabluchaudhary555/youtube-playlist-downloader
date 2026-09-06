#!/usr/bin/env python3
"""
Archive revalidation for the YouTube Playlist Downloader.
-----------------------------------------------------------
Problem: yt-dlp records a video as "downloaded" in the archive file
as soon as the raw download finishes -- BEFORE the ffmpeg merge step
completes. If the merge fails/gets interrupted, the archive still
says "done", so future runs skip that video forever even though its
final .mp4 was never created (or was deleted by
cleanup_broken_merges.py).

This script:
  1. Reads the playlist (using yt-dlp, fast "flat" mode -- no downloading)
  2. For each video, checks whether a matching "<index> - ....mp4" file
     actually exists in your playlist folder
  3. If it's missing, removes that video's entry from downloaded_archive.txt
  4. After this, re-running yt_playlist_downloader.py will properly
     re-download + merge only the truly missing episodes.

Run this any time after cleanup_broken_merges.py, or whenever you
suspect the archive and the actual downloaded files are out of sync.

Usage:
    python revalidate_downloads.py "<playlist_url>" "<path to playlist folder>"
"""

import sys
import os

try:
    import yt_dlp
except ImportError:
    print("yt-dlp is not installed. Install it first with:")
    print("    pip install -r requirements.txt")
    sys.exit(1)


def revalidate(playlist_url: str, folder: str):
    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}")
        sys.exit(1)

    archive_path = os.path.join(folder, "downloaded_archive.txt")
    if not os.path.exists(archive_path):
        # The downloader script actually saves the archive one level up
        # (in the base "downloads" folder), not inside the playlist's
        # own subfolder. Check there too.
        parent_path = os.path.join(os.path.dirname(folder.rstrip("\\/")), "downloaded_archive.txt")
        if os.path.exists(parent_path):
            archive_path = parent_path
        else:
            print("No archive file found at either:")
            print(f"  {os.path.join(folder, 'downloaded_archive.txt')}")
            print(f"  {parent_path}")
            print("Nothing to fix -- just run the downloader normally.")
            return

    print("Fetching playlist info (fast mode, no downloading)...")
    ydl_opts = {"extract_flat": True, "quiet": True, "ignoreerrors": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    entries = info.get("entries", [])
    existing_files = os.listdir(folder)

    # Read current archive lines
    with open(archive_path, "r", encoding="utf-8") as f:
        archive_lines = [line.strip() for line in f if line.strip()]

    ids_to_remove = set()
    missing_count = 0

    for idx, entry in enumerate(entries, start=1):
        if entry is None:
            continue
        video_id = entry.get("id")
        if not video_id:
            continue

        prefix = f"{idx:02d} - "
        found = any(
            fn.startswith(prefix) and fn.lower().endswith(".mp4")
            for fn in existing_files
        )

        if not found:
            missing_count += 1
            ids_to_remove.add(video_id)
            print(f"  Episode {idx}: mp4 missing -> will retry (id: {video_id})")

    # Filter out archive lines whose id is in ids_to_remove
    new_lines = []
    removed_count = 0
    for line in archive_lines:
        parts = line.split()
        line_id = parts[-1] if parts else ""
        if line_id in ids_to_remove:
            removed_count += 1
            continue
        new_lines.append(line)

    with open(archive_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + ("\n" if new_lines else ""))

    print("\n---- Summary ----")
    print(f"Episodes missing their .mp4: {missing_count}")
    print(f"Archive entries removed: {removed_count}")
    if missing_count:
        print("\nNow re-run yt_playlist_downloader.py with the same playlist URL --")
        print("these episodes will be properly re-downloaded and merged this time.")
    else:
        print("\nEverything checks out -- no missing episodes found.")


def main():
    if len(sys.argv) >= 3:
        url = sys.argv[1]
        folder = sys.argv[2]
    else:
        url = input("Enter the playlist URL: ").strip()
        folder = input("Enter the path to your playlist folder: ").strip().strip('"')

    revalidate(url, folder)


if __name__ == "__main__":
    main()