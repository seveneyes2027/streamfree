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

if not music_path.exists():
    print("දෝෂයකි: music නමින් ෆෝල්ඩරයක් හමු නොවීය!")
    exit(1)

# music ෆෝල්ඩරේ ඇති සියලුම MP3 ෆයිල්ස් සොයාගෙන spaces/brackets නැතිව song1.mp3, song2.mp3 ලෙස Rename කිරීම
raw_files = sorted(list(music_path.glob("*.mp3")))
clean_files = []

if not raw_files:
    print("අපහසුතාවයක්: music/ ෆෝල්ඩරේ තුළ MP3 ගොනු හමු නොවීය!")
    exit(1)

print(f"හමුවූ ගීත සංඛ්‍යාව: {len(raw_files)}")

for i, file in enumerate(raw_files, start=1):
    new_name = music_path / f"song{i}.mp3"
    try:
        if file != new_name:
            if new_name.exists():
                new_name.unlink()
            file.rename(new_name)
        clean_files.append(new_name)
    except Exception as e:
        print(f"Rename දෝෂයක්: {e}")
        clean_files.append(file)

# FFmpeg සඳහා audio inputs සකස් කිරීම
audio_inputs = []
for song in clean_files:
    abs_path = song.resolve().as_posix()
    audio_inputs.extend(["-stream_loop", "-1", "-i", abs_path])

# සිංදු එකින් එක පිළිවෙළට ප්ලේ වීමට filter එක සැකසීම
inputs_mapping = "".join([f"[{i}:a]" for i in range(1, len(clean_files) + 1)])
filter_complex_str = f"{inputs_mapping}concat=n={len(clean_files)}:v=0:a=1[outa]"

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
