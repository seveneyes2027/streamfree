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

# Tmpfiles Direct Links
MUSIC_URLS = [
    "https://tmpfiles.org/dl/w8AL6lbnwvPO/13.mp3",
    "https://tmpfiles.org/dl/wAAf6dbJeYw6/15.mp3",
    "https://tmpfiles.org/dl/wgAv6Cbkf3KP/17.mp3"
]

valid_files = []

print("අන්තර්ජාලයෙන් ගීත බාගත කරමින් පවතී...")
for i, url in enumerate(MUSIC_URLS, start=1):
    file_path = music_path / f"song{i}.mp3"
    try:
        # Browser එකක් වගේ පෙනී සිටිමින් Redirects සමඟ ඩවුන්ලෝඩ් කිරීම
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'audio/mpeg,application/octet-stream,*/*'
            }
        )
        
        # urlopen මඟින් ස්වයංක්‍රීයව redirect වෙන තැන් වලට ගොස් ෆයිල් එක ඩවුන්ලෝඩ් කර ගනී
        with urllib.request.urlopen(req) as response:
            content = response.read()
            
            # HTML පිටුවක් ඇවිත්දැයි බැලීම
            if b"<!DOCTYPE html>" in content or b"<html" in content:
                print(f"දෝෂයකි (song{i}): තවමත් වෙබ් පිටුවක් ලැබෙයි!")
                continue
                
            with open(file_path, 'wb') as out_file:
                out_file.write(content)

        if file_path.stat().st_size > 50000:
            valid_files.append(file_path)
            print(f"song{i}.mp3 සාර්ථකව බාගත කරන ලදී.")
        else:
            print(f"අවවාදයයි: song{i}.mp3 ගොනුව ඉතා කුඩායි හෝ හානි වී ඇත.")
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
