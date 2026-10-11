import os
import subprocess
import time
from pathlib import Path
import urllib.request

STREAM_KEY = os.environ.get("YOUTUBE_STREAM_KEY")
VIDEO_FILE = "video.mp4"
MUSIC_DIR = "music"

if not STREAM_KEY:
    print("දෝෂයකි: YOUTUBE_STREAM_KEY සැට් කර නැත!")
    exit(1)

rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
music_path = Path(MUSIC_DIR)
music_path.mkdir(exist_ok=True)

# ඔබ ලබා දුන් Gofile සෘජු ලින්ක් 3
MUSIC_URLS = [
    "https://store9.gofile.io/download/web/5ab12ca6-d58f-443d-9ab1-356f930a9422/1%20(1).mp3",
    "https://store5.gofile.io/download/web/c6138f14-ac4f-40fc-9b71-c88f0df71f75/1%20(2).mp3",
    "https://store9.gofile.io/download/web/078db7f8-3a5f-4777-9d7b-3fbdeea849f9/1%20(4).mp3"
]

valid_files = []

print("අන්තර්ජාලයෙන් ගීත බාගත කරමින් සහ නම් සකස් කරමින් පවතී...")
for i, url in enumerate(MUSIC_URLS, start=1):
    # වරහන් සහ spaces රහිතව song1.mp3, song2.mp3 ලෙස සුරැකේ
    file_path = music_path / f"song{i}.mp3"
    try:
        urllib.request.urlretrieve(url, file_path)
        if file_path.stat().st_size > 1024:
            valid_files.append(file_path)
            print(f"song{i}.mp3 සාර්ථකව බාගත කරන ලදී.")
        else:
            print(f"අවවාදයයි: song{i}.mp3 ගොනුව හානි වී ඇත.")
    except Exception as e:
        print(f"බාගත කිරීමේ දෝෂයක් (song{i}): {e}")

if not valid_files:
    print("දෝෂයකි: කිසිදු ගීතයක් බාගත කරගත නොහැකි විය!")
    exit(1)

# FFmpeg සඳහා audio inputs සකස් කිරීම
audio_inputs = []
for song in valid_files:
    abs_path = song.resolve().as_posix()
    audio_inputs.extend(["-stream_loop", "-1", "-i", abs_path])

inputs_mapping = "".join([f"[{i}:a]" for i in range(1, len(valid_files) + 1)])
filter_complex_str = f"{inputs_mapping}concat=n={len(valid_files)}:v=0:a=1[outa]"

# FFmpeg ස්ට්‍රීම් විධානය
command = [
    "ffmpeg",
    "-re",
    "-stream_loop", "-1", "-i", VIDEO_FILE,     # වීඩියෝ එක දිගටම Loop වේ
] + audio_inputs + [
    "-filter_complex", filter_complex_str,
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
    "-map", "[outa]",
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
