# YouTube Playlist Downloader

A simple Python CLI toolkit to download entire YouTube playlists using [yt-dlp](https://github.com/yt-dlp/yt-dlp), with automatic video+audio merging via ffmpeg — plus two helper scripts to recover cleanly from interrupted downloads (laptop shutdowns, network drops, failed merges, etc.).

## Project Structure

```
youtube-playlist-downloader/
├── yt_playlist_downloader.py    # Main script — downloads the playlist
├── cleanup_broken_merges.py     # Helper — removes leftover files from failed merges
├── revalidate_downloads.py      # Helper — fixes the archive so retried episodes aren't skipped
├── requirements.txt
├── .gitignore
└── README.md
```

## Features

- Downloads all videos in a YouTube playlist in one go
- Automatically merges video and audio into a single `.mp4` file (no separate `.webm`/audio-only files)
- Caps video quality at **720p** — falls back to the lowest available quality if 720p isn't offered for a video
- Optional **audio-only (MP3)** download mode
- Skips unavailable/private videos instead of stopping the whole batch
- **Resume support** — if the download is interrupted (laptop shuts down, power cut, etc.), re-running the script picks up where it left off instead of starting from scratch
- Saves files into a playlist-named folder, numbered in order
- Live download progress shown in the terminal

## Requirements

- Python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **ffmpeg** (required for merging video + audio into one file)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/youtube-playlist-downloader.git
   cd youtube-playlist-downloader
   ```
2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install ffmpeg (see setup guide below).

## ffmpeg Setup (Windows)

ffmpeg is required — without it, video and audio download as separate files instead of merging.

### Option A: Using winget
```bash
winget install ffmpeg
```
Run this in an **Administrator** Command Prompt to avoid permission errors. Restart your terminal after installation.

### Option B: Manual install
1. Download `ffmpeg-release-essentials.zip` from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/#release-builds).
2. Extract it and move the extracted folder to `C:\ffmpeg` (so `C:\ffmpeg\bin\ffmpeg.exe` exists).
3. Add `C:\ffmpeg\bin` to your system PATH:
   - Press `Win` → search "Environment Variables" → open "Edit the system environment variables"
   - Click **Environment Variables** → under **System variables**, select `Path` → **Edit** → **New**
   - Paste `C:\ffmpeg\bin` → OK on all windows
4. Open a **new** terminal and verify:
   ```bash
   ffmpeg -version
   ```
   You should see version info printed (no "not recognized" error).

### macOS / Linux
```bash
# macOS
brew install ffmpeg

# Linux (Debian/Ubuntu)
sudo apt install ffmpeg
```

## Usage

### 1. Downloading a playlist

Run the script:
```bash
python yt_playlist_downloader.py
```
Then paste the playlist URL when prompted, and choose whether you want audio-only (`y`) or the full video with merged audio (`N` / Enter).

Or pass the URL directly as an argument:
```bash
python yt_playlist_downloader.py "https://www.youtube.com/playlist?list=XXXXXXXX"
```

Downloaded files are saved to:
```
downloads/<playlist name>/01 - Video Title.mp4
downloads/<playlist name>/02 - Video Title.mp4
...
```

A `downloaded_archive.txt` file is also created inside the `downloads/` folder (one level above the playlist subfolder). This is what powers resume support — **don't delete or move it** if you plan to resume later.

### 2. If your laptop shuts down / the download gets interrupted

Just run the same command again with the same playlist URL:
```bash
python yt_playlist_downloader.py
```
yt-dlp checks `downloaded_archive.txt` and skips everything already downloaded, continuing from where it stopped.

### 3. If some episodes end up with only `.webm`/`.part` files (merge failed)

Sometimes the download finishes but the ffmpeg merge into `.mp4` gets interrupted (e.g. the process was killed mid-merge). This leaves leftover `.webm`/`.part` files with no final `.mp4`. Fix it in two steps:

**Step A — clean up the leftovers:**
```bash
python cleanup_broken_merges.py "downloads/<playlist folder name>"
```
This scans the folder, finds episodes with no final `.mp4`, and deletes their leftover files.

**Step B — revalidate the archive:**
```bash
python revalidate_downloads.py "<playlist_url>" "downloads/<playlist folder name>"
```
This is the important step. yt-dlp's archive file marks a video as "downloaded" as soon as the raw download finishes — **before** the merge step. So even after Step A deletes the leftover files, the archive still thinks those episodes are done, and will skip them again. `revalidate_downloads.py` checks the archive against what's actually in the folder and removes the incorrect entries, so those specific episodes will be properly retried.

**Step C — re-run the downloader:**
```bash
python yt_playlist_downloader.py
```
Only the genuinely missing/broken episodes will be downloaded and merged this time; everything else is skipped.

## Disclaimer

This tool is intended for downloading your own content, public-domain content, or content whose license/terms permit downloading. Downloading copyrighted videos without permission may violate YouTube's Terms of Service and applicable copyright law. Use responsibly.

## Tech Stack

- Python
- yt-dlp
- ffmpeg