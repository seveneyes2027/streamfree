import os
import subprocess
import time

# YouTube Stream Key එක Environment variable එකෙන් ලබා ගැනීම
STREAM_KEY = os.environ.get("YOUTUBE_STREAM_KEY")
VIDEO_FILE = "video.mp4"  # ඔයා අප්ලෝඩ් කරපු වීඩියෝ එකේ නම

if not STREAM_KEY:
    print("දෝෂයකි: YOUTUBE_STREAM_KEY එක සෙට් කර නැත!")
    exit(1)

# YouTube RTMP URL එක
rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"

# FFmpeg මගින් වීඩියෝ එක දිගටම ලූප් කරමින් යැවීමේ විධානය
command = [
    "ffmpeg",
    "-re",
    "-stream_loop", "-1",
    "-i", VIDEO_FILE,
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-b:v", "3000k",
    "-maxrate", "3000k",
    "-bufsize", "6000k",
    "-pix_fmt", "yuv420p",
    "-g", "60",
    "-c:a", "aac",
    "-b:a", "128k",
    "-ar", "44100",
    "-f", "flv",
    rtmp_url
]

print("ස්ට්‍රීම් වීම ආරම්භ වේ...")
while True:
    process = subprocess.Popen(command)
    process.wait()
    print("සම්බන්ධතාවය බිඳ වැටුණි, නැවත ආරම්භ කරමින් පවතී...")
    time.sleep(5)
