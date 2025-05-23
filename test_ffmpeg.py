from pydub.utils import which
from pydub import AudioSegment
import os
import configparser
import sys

config = configparser.ConfigParser()
config.read('config.conf')
# 🔧 Set paths BEFORE importing AudioSegment
# Set paths BEFORE importing AudioSegment
ffmpeg_path = config.get('paths', 'ffmpeg_path', fallback=None)
if ffmpeg_path is None or not ffmpeg_path.strip(): # Also check for empty string
    print('Error: ffmpeg_path is not configured in the CONF file.', file=sys.stderr)
    raise ValueError('Need to configure ffmpeg_path in order to run this script.')

ffprobe_path = config.get('paths', 'ffmpeg_probe', fallback=None)
if ffprobe_path is None or not ffprobe_path.strip(): # Also check for empty string
    print('Error: ffprobe_path is not configured in the CONF file.', file=sys.stderr)
    raise ValueError('Need to configure ffprobe_path in order to run this script.')
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)  # Add to PATH at runtime

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path
from gtts import gTTS
mp3_path = r".\output\Tell-Tale_Heart_mp3_part_1.mp3"
tts = gTTS("Part 1", lang="en")
tts.save(mp3_path)
if not os.path.exists(mp3_path):
    raise FileNotFoundError(f"MP3 file not found: {mp3_path}")
audio = AudioSegment.from_mp3(mp3_path)
print("✅ MP3 loaded successfully!")
