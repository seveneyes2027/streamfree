import os
import subprocess
import time
from pathlib import Path

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

# ස්මාර්ට් ක්‍රමය: ෆයිල් නම්වල spaces, brackets වගේ ප්‍රශ්න මඟහරවා ගැනීමට 
# ෆෝල්ඩරේ ඇති සියලුම MP3 ෆයිල්ස් පිළිවෙළකට අලුත් නම්වලට (track_1.mp3, track_2.mp3...) ස්වයංක්‍රීයව Rename කිරීම
raw_music_files = sorted(list(music_path.glob("*.mp3")))

if not raw_music_files:
    print("අපහසුතාවයක්: music/ ෆෝල්ඩරේ තුළ MP3 ගොනු හමු නොවීය!")
    exit(1)

print(f"හමුවූ ගීත සංඛ්‍යාව: {len(raw_music_files)}")

renamed_music_files = []
for index, song in enumerate(raw_music_files, start=1):
    new_name = music_path / f"track_{index}.mp3"
    try:
        # දැනටමත් rename වී නැත්නම් හෝ නම වෙනස් නම් rename කරන්න
        if song != new_name:
            if new_name.exists():
                new_name.unlink()
            song.rename(new_name)
        renamed_music_files.append(new_name)
    except Exception as e:
        print(f"ගොනුව නම් කිරීමේ දෝෂයක් ({song.name}): {e}")
        renamed_music_files.append(song) # බැරි වුණොත් මුල් නමම පාවිච්චි කරයි

# FFmpeg සඳහා concat.txt ෆයිල් එක සෑදීම
with open(CONCAT_FILE, "w", encoding="utf-8") as f:
    for song in renamed_music_files:
        abs_path = song.resolve().as_posix()
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
