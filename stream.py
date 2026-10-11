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

# ෆෝල්ඩරේ ඇති MP3 ෆයිල්ස් පරීක්ෂා කර valid ඒවා පමණක් තෝරා ගැනීම
raw_files = sorted(list(music_path.glob("*.mp3")))
valid_files = []

if not raw_files:
    print("අපහසුතාවයක්: music/ ෆෝල්ඩරේ තුළ MP3 ගොනු හමු නොවීය!")
    exit(1)

for i, file in enumerate(raw_files, start=1):
    new_name = music_path / f"song{i}.mp3"
    try:
        if file != new_name:
            if new_name.exists():
                new_name.unlink()
            file.rename(new_name)
        
        # ෆයිල් එකේ සැබෑ ප්‍රමාණය (size) බැලීම (KB 1 කට වඩා වැඩි විය යුතුය)
        if new_name.stat().st_size > 1024:
            valid_files.append(new_name)
        else:
            print(f"අවවාදයයි: {new_name.name} ගොනුව ඉතා කුඩායි හෝ හානි වී ඇත.")
    except Exception as e:
        print(f"දෝෂයක් ({file.name}): {e}")

if not valid_files:
    print("දෝෂයකි: භාවිත කළ හැකි කිසිදු නිවැරදි MP3 ගොනුවක් හමු නොවීය!")
    exit(1)

print(f"සාර්ථකව එකතු කළ ගීත සංඛ්‍යාව: {len(valid_files)}")

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
