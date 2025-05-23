from pydub.utils import which
from pydub import AudioSegment
import os

# 🔧 Set paths BEFORE importing AudioSegment
ffmpeg_path = r"C:\Users\bradley.eylander\OneDrive - LMI Consulting\Documents\Python\ffmpeg-2025-05-19-git-c55d65ac0a-full_build\bin\ffmpeg.exe"
ffprobe_path = r"C:\Users\bradley.eylander\OneDrive - LMI Consulting\Documents\Python\ffmpeg-2025-05-19-git-c55d65ac0a-full_build\bin\ffprobe.exe"

os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)  # Add to PATH at runtime

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path
from gtts import gTTS
mp3_path = r"C:\Users\bradley.eylander\OneDrive - LMI Consulting\Documents\Personal\equity\amr_audio\intro_part_1.mp3"
tts = gTTS("Part 1", lang="en")
tts.save(mp3_path)
if not os.path.exists(mp3_path):
    raise FileNotFoundError(f"MP3 file not found: {mp3_path}")
audio = AudioSegment.from_mp3(mp3_path)
print("✅ MP3 loaded successfully!")
