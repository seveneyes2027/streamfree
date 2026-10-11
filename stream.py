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

# කිසිදු දෝෂයකින් තොරව ක්ෂණිකව ඩවුන්ලෝඩ් වන සෘජු MP3 ලින්ක් (Direct MP3 Links)
MUSIC_URLS = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
]

valid_files = []

print("අන්තර්ජාලයෙන් ගීත ඩවුන්ලෝඩ් කරමින් පවතී...")
for i, url in enumerate(MUSIC_URLS, start=1):
    file_path = music_path / f"song{i}.mp3"
    try:
        urllib.request.urlretrieve(url, file_path)
        if file_path.stat().st_size > 1024:
            valid_files.append(file_path)
            print(f"song{i}.mp3 සාර්ථකව බාගත කරන ලදී.")
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
