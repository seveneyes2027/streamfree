import os
import subprocess
import time
from pathlib import Path

STREAM_KEY = os.environ.get("YOUTUBE_STREAM_KEY")
VIDEO_FILE = "video2.mp4"
PLAYLIST_FILE = "playlist.txt"

if not STREAM_KEY:
    print("දෝෂයකි: YOUTUBE_STREAM_KEY සැට් කර නැත!")
    exit(1)

rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"

# Root එකේ ඇති සියලුම MP3 ෆයිල්ස් ස්වයංක්‍රීයව අල්ලා ගැනීම
music_files = sorted([p for p in Path(".").glob("*.mp3") if p.name != "video.mp4"])

if not music_files:
    print("දෝෂයකි: කිසිදු MP3 ගොනුවක් හමු නොවීය! කරුණාකර Root Folder එකට MP3 එකතු කරන්න.")
    exit(1)

print(f"හමුවූ ගීත සංඛ්‍යාව: {len(music_files)}")
for song in music_files:
    print(f"- Found: {song.name}")

# FFmpeg concat filter එක සඳහා playlist.txt ගොනුව සෑදීම
with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
    for song in music_files:
        abs_path = song.resolve().as_posix()
        f.write(f"file '{abs_path}'\n")

# FFmpeg ස්ට්‍රීම් විධානය (30 FPS, 10,000kbps video, 320k high-quality audio, looping playlist)
command = [
    "ffmpeg",
    "-re",
    "-stream_loop", "-1", "-i", VIDEO_FILE,
    "-f", "concat",
    "-safe", "0",
    "-stream_loop", "-1", "-i", PLAYLIST_FILE,
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-b:v", "10000k",
    "-maxrate", "10000k",
    "-bufsize", "20000k",
    "-pix_fmt", "yuv420p",
    "-r", "30",          # 30 FPS
    "-g", "60",          # 30 FPS සඳහා Keyframe interval එක 60
    "-c:a", "aac",
    "-b:a", "320k",      # High Quality 320kbps Audio
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-shortest",
    "-f", "flv",
    rtmp_url
]

print("30 FPS, 10,000kbps සහ 320kbps උසස් ශ්‍රව්‍ය සමඟ ස්ට්‍රීම් වීම ආරම්භ වේ...")
while True:
    process = subprocess.Popen(command)
    process.wait()
    print("සම්බන්ධතාවය බිඳ වැටුණි, නැවත ආරම්භ කරමින් පවතී...")
    time.sleep(5)
