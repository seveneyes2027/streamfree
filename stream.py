import os
import subprocess
import time
from pathlib import Path

STREAM_KEY = os.environ.get("YOUTUBE_STREAM_KEY")
VIDEO_FILE = "video.mp4"
MUSIC_DIR = "music"

if not STREAM_KEY:
    print("දෝෂයකි: YOUTUBE_STREAM_KEY සැට් කර නැත!")
    exit(1)

rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
music_path = Path(MUSIC_DIR)
music_path.mkdir(exist_ok=True)

# Vocaroo සෘජු MP3 ලින්ක්ස් මෙහි ඇතුළත් කරන්න (අවශ්‍ය නම් තවත් ලින්ක් එකතු කළ හැක)
MUSIC_URLS = [
    "https://media1.vocaroo.com/mp3/1ippMrqt7gUe",
    # "තවත්_සිංදුවක_ඩිරෙක්ට්_ලින්ක්_එකක්_නම්_මෙතැනට_දාන්න"
]

valid_files = []

print("ගීත බාගත කරමින් පවතී...")
for i, url in enumerate(MUSIC_URLS, start=1):
    file_path = music_path / f"song{i}.mp3"
    
    # wget හරහා ඩවුන්ලෝඩ් කිරීම
    cmd = ["wget", "-O", str(file_path), url]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if file_path.exists() and file_path.stat().st_size > 1024:
        valid_files.append(file_path)
        print(f"song{i}.mp3 සාර්ථකව ලබා ගන්නා ලදී.")
    else:
        print(f"අවවාදයයි: song{i}.mp3 ලබා ගැනීමට නොහැකි විය.")

if not valid_files:
    print("දෝෂයකි: කිසිදු ගීතයක් ලබාගත නොහැකි විය!")
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
    "-stream_loop", "-1", "-i", VIDEO_FILE,
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
