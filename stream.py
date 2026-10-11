import os
import subprocess
import time
from pathlib import Path

STREAM_KEY = os.environ.get("YOUTUBE_STREAM_KEY")
VIDEO_FILE = "video.mp4"
MUSIC_DIR = "music"

if not STREAM_KEY:
    print("දෝෂයකි: YOUTUBE_STREAM_KEY environment variable එක සෙට් කර නැත!")
    exit(1)

rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"

music_path = Path(MUSIC_DIR)
if not music_path.exists():
    print("දෝෂයකි: music නමින් ෆෝල්ඩරයක් හමු නොවීය!")
    exit(1)

# music ෆෝල්ඩරයේ ඇති සියලුම MP3 ෆයිල්ස් ලබා ගැනීම (නම කුමක් වුවත්)
music_files = sorted(list(music_path.glob("*.mp3")))

if not music_files:
    print("අපහසුතාවයක්: music/ ෆෝල්ඩරේ තුළ MP3 ගොනු හමු නොවීය!")
    exit(1)

print(f"හමුවූ ගීත සංඛ්‍යාව: {len(music_files)}")

# FFmpeg සඳහා audio inputs සකස් කිරීම (සෑම සිංදුවක්ම -stream_loop -1 මඟින් අනන්තවත් ලූප් වේ)
audio_inputs = []
for song in music_files:
    abs_path = song.resolve().as_posix()
    audio_inputs.extend(["-stream_loop", "-1", "-i", abs_path])

# සිංදු සියල්ල එකින් එක පිළිවෙළට ප්ලේ වීමට (concat) FFmpeg filter එක සැකසීම
# [1:a][2:a][3:a][4:a] concat=n=4:v=0:a=1 [outa]
inputs_mapping = "".join([f"[{i}:a]" for i in range(1, len(music_files) + 1)])
filter_complex_str = f"{inputs_mapping}concat=n={len(music_files)}:v=0:a=1[outa]"

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
