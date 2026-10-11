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

# music ෆෝල්ඩරේ ඇතුළේ තියෙන MP3 ෆයිල්ස් සෙවීම
music_files = sorted([str(p) for p in Path(MUSIC_DIR).glob("*.mp3")])

if not music_files:
    print("අපහසුතාවයක්: music/ ෆෝල්ඩරේ තුළ MP3 ගොනු හමු නොවීය! මුල් ශ්‍රව්‍ය සමඟ ස්ට්‍රීම් වේ.")
    # සිංදු නැත්නම් පරණ ක්‍රමයටම anullsrc පාවිච්චි කරයි
    audio_inputs = ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    filter_complex = []
else:
    print(f"හමුවූ ගීත සංඛ්‍යාව: {len(music_files)}")
    audio_inputs = []
    for song in music_files:
        audio_inputs.extend(["-stream_loop", "-1", "-i", song])
    
    # සියලුම සිංදු එකින් එක ප්ලේ වෙන්න (concat) FFmpeg filter එක සැකසීම
    inputs_str = "".join([f"[{i}:a]" for i in range(1, len(music_files) + 1)])
    filter_complex = [
        "-filter_complex", 
        f"{inputs_str}concat=n={len(music_files)}:v=0:a=1[outa]",
        "-map", "0:v",
        "-map", "[outa]"
    ]

# FFmpeg ලූප් ස්ට්‍රීම් විධානය
command = [
    "ffmpeg",
    "-re",
    "-stream_loop", "-1",
    "-i", VIDEO_FILE,
] + audio_inputs + filter_complex + [
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-b:v", "3000k",
    "-maxrate", "3000k",
    "-bufsize", "6000k",
    "-pix_fmt", "yuv420p",
    "-g", "60",
    "-c:a", "aac",
    "-b:a", "128k",
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
