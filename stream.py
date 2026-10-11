import os
import subprocess
import time
from pathlib import Path
import re

STREAM_KEY = os.environ.get("YOUTUBE_STREAM_KEY")
VIDEO_FILE = "video.mp4"
MUSIC_DIR = "music"
CONCAT_FILE = "concat.txt"

if not STREAM_KEY:
    print("දෝෂයකි: YOUTUBE_STREAM_KEY environment variable එක සෙට් කර නැත!")
    exit(1)

rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"

music_path = Path(MUSIC_DIR)
if not music_path.exists():
    print(f"දෝෂයකි: {MUSIC_DIR} නමින් ෆෝල්ඩරයක් හමු නොවීය!")
    exit(1)

# music ෆෝල්ඩරයේ ඇති සියලුම MP3 ෆයිල්ස් ලබා ගැනීම
raw_music_files = sorted(list(music_path.glob("*.mp3")))

if not raw_music_files:
    print("අපහසුතාවයක්: music/ ෆෝල්ඩරේ තුළ MP3 ගොනු හමු නොවීය!")
    exit(1)

print(f"හමුවූ මුල් ගීත සංඛ්‍යාව: {len(raw_music_files)}")

# Smart Fix: ෆයිල් නම්වල ගැටලු (spaces, brackets) මඟහරවා ගැනීමට 
# ඒවා temporary safe paths ලෙස concat.txt වෙත ලිවීම
with open(CONCAT_FILE, "w", encoding="utf-8") as f:
    for song in raw_music_files:
        # Absolute path එක ලබා ගැනීම
        abs_path = song.resolve().as_posix()
        # FFmpeg concat format එකට අනුව ලියයි
        f.write(f"file '{abs_path}'\n")

# FFmpeg ස්ට්‍රීම් විධානය
command = [
    "ffmpeg",
    "-re",
    "-stream_loop", "-1", "-i", VIDEO_FILE,                     # වීඩියෝ එක දිගටම Loop වේ
    "-stream_loop", "-1", "-f", "concat", "-safe", "0", "-i", CONCAT_FILE, # MP3 සියල්ල පිළිවෙලට එකින් එක Loop වේ
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-b:v", "3000k",
    "-maxrate", "3000k",
    "-bufsize", "6000k",
    "-pix_fmt", "yuv420p",
    "-g", "60",
    "-c:a", "aac",
    "-b:a", "128k",
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-shortest",
    "-f", "flv",
    rtmp_url
]

print("ස්ට්‍රීම් වීම ආරම්භ වේ...")
while True:
    process = subprocess.Popen(command)
    process.wait()
    print("සම්බන්ධතාවය බිඳ වැටුණි, නැවත ආරම්භ කරමින් පවතී...")
    time.sleep(5)
