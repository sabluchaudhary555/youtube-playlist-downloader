#!/usr/bin/env python3
"""

NOTE: This script only cleans up leftover files. If the download
archive (downloaded_archive.txt) already marked those episodes as
"downloaded" before the merge failed, you'll also need to run
revalidate_downloads.py afterwards — otherwise yt-dlp will skip
those episodes again instead of retrying them.

Usage:
    python cleanup_broken_merges.py "downloads/<playlist folder name>"
"""

import sys
import os
from collections import defaultdict

LEFTOVER_EXTENSIONS = {".webm", ".part", ".m4a", ".ytdl", ".temp"}


def get_base_name(filename: str) -> str:
    """Strip the extension to get the 'episode identity' part of the filename."""
    return os.path.splitext(filename)[0]


def cleanup_folder(folder: str):
    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}")
        sys.exit(1)

    files = os.listdir(folder)

    # Group all files by their base name (without extension)
    groups = defaultdict(list)
    for f in files:
        full_path = os.path.join(folder, f)
        if os.path.isfile(full_path):
            base = get_base_name(f)
            groups[base].append(f)

    deleted_count = 0
    incomplete_episodes = []

    for base, group_files in groups.items():
        has_mp4 = any(f.lower().endswith(".mp4") for f in group_files)
        has_leftover = any(
            os.path.splitext(f)[1].lower() in LEFTOVER_EXTENSIONS for f in group_files
        )

        if has_leftover and not has_mp4:
            # This episode never finished merging — delete the leftovers
            incomplete_episodes.append(base)
            for f in group_files:
                path = os.path.join(folder, f)
                try:
                    os.remove(path)
                    deleted_count += 1
                    print(f"  Deleted leftover: {f}")
                except OSError as e:
                    print(f"  Could not delete {f}: {e}")

    print("\n---- Summary ----")
    if incomplete_episodes:
        print(f"Found {len(incomplete_episodes)} incomplete episode(s):")
        for ep in incomplete_episodes:
            print(f"  - {ep}")
        print(f"\nDeleted {deleted_count} leftover file(s).")
        print("\nNext step: run revalidate_downloads.py so the archive file")
        print("doesn't skip these episodes, then re-run yt_playlist_downloader.py.")
    else:
        print("No broken/incomplete episodes found. Everything looks properly merged!")


def main():
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        folder = input("Enter the path to your playlist folder: ").strip().strip('"')

    cleanup_folder(folder)


if __name__ == "__main__":
    main()