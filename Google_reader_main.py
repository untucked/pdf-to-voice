from gtts import gTTS
import pdfplumber
import os
import textwrap
from pydub import AudioSegment
import tempfile
from datetime import timedelta
import re
import time
import configparser

config = configparser.ConfigParser()
config.read('config.conf')

# local
import support

# Set paths BEFORE importing AudioSegment
ffmpeg_path = config.get('paths', 'ffmpeg_path', fallback=None)
ffprobe_path = config.get('paths', 'ffmpeg_probe', fallback=None)
if ffmpeg_path==None:
    print('Need to install ffmpeg and ffprobe in order to run this')
    SystemError()

os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)  # Add to PATH at runtime

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# === CONFIG ===
pdf_path = config.get('read', 'read_essay', fallback='the-essays-of-warren-buffett_preface.pdf')
output_dir = config.get('read', 'output_dir', fallback='output')
chunk_size = 4900  # Safe limit for gTTS (under 5000)

os.makedirs(output_dir, exist_ok=True)

# === EXTRACT TEXT FROM PDF ===
full_text = support.get_full_text(pdf_path)

# === SPLIT INTO CHUNKS ===
chunks = textwrap.wrap(full_text, chunk_size, break_long_words=False, break_on_hyphens=False)

# === CONVERT EACH CHUNK TO MP3 ===
mp3_name='mp3_output'
support.convert_to_mp3(chunks, output_dir, name=mp3_name,
                   test_script=False)

# === MERGE ALL MP3 FILES ===
support.merge_mp3s(AudioSegment, mp3_name, output_dir=output_dir,clean_mp3s=False)

