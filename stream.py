import os
import subprocess
import time
from pathlib import Path

STREAM_KEY = os.environ.get("YOUTUBE_STREAM_KEY")
VIDEO_FILE = "video.mp4"

if not STREAM_KEY:
    print("දෝෂයකි: YOUTUBE_STREAM_KEY සැට් කර නැත!")
    exit(1)

rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"

# GitHub එකේ root folder එකේ (ප්‍රධාන තැන) තියෙන සියලුම MP3 ෆයිල්ස් ස්වයංක්‍රීයව සොයා ගැනීම
music_files = sorted([p for p in Path(".").glob("*.mp3") if p.name != "video.mp4"])

if not music_files:
    print("දෝෂයකි: කිසිදු MP3 ගොනුවක් හමු නොවීය!")
    exit(1)

print(f"හමුවූ ගීත සංඛ්‍යාව: {len(music_files)}")

# FFmpeg සඳහා audio inputs සකස් කිරීම
audio_inputs = []
for song in music_files:
    abs_path = song.resolve().as_posix()
    audio_inputs.extend(["-stream_loop", "-1", "-i", abs_path])

inputs_mapping = "".join([f"[{i}:a]" for i in range(1, len(music_files) + 1)])
filter_complex_str = f"{inputs_mapping}concat=n={len(music_files)}:v=0:a=1[outa]"

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
