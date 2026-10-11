import subprocess
import time

# ඔයාගේ Stream Key එක මෙහි සටහන් කර ඇත
STREAM_KEY = "s0v9-q454-v2xr-bcm3-86fd"
VIDEO_FILE = "video.mp4"

if not STREAM_KEY or STREAM_KEY == "YOUR_REAL_STREAM_KEY_HERE":
    print("දෝෂයකි: කරුණාකර කෝඩ් එකේ නිවැරදි Stream Key එක ඇතුළත් කරන්න!")
    exit(1)

# YouTube RTMP URL එක
rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"

# FFmpeg ලූප් ස්ට්‍රීම් විධානය (සවුන්ඩ් නැති වීඩියෝ සඳහා ස්වයංක්‍රීයව Audio එකක් ජනනය කරයි)
command = [
    "ffmpeg",
    "-re",
    "-stream_loop", "-1",
    "-i", VIDEO_FILE,
    "-f", "lavfi",
    "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
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
