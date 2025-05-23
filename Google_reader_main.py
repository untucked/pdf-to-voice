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
import sys

config = configparser.ConfigParser()
config.read('config.conf')

# local
import support

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

# === CONFIG ===
pdf_path = config.get('read', 'read_essay', fallback='Tell-Tale_Heart.pdf')
# pdf_path = config.get('read', 'read_essay', fallback='picture_pdf_text.pdf')
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"❌ PDF not found at: {pdf_path}")
output_dir = config.get('read', 'output_dir', fallback='output')
chunk_size = 4900  # Safe limit for gTTS (under 5000)

os.makedirs(output_dir, exist_ok=True)

# === EXTRACT TEXT FROM PDF ===
full_text = support.get_full_text(pdf_path)

# === SPLIT INTO CHUNKS ===
chunks = textwrap.wrap(full_text, chunk_size, break_long_words=False, break_on_hyphens=False)

# === CONVERT EACH CHUNK TO MP3 ===
# Get the base name (filename with extension, but no directory)
base_name = os.path.basename(pdf_path)
# Split the base name into name and extension
file_name_without_extension, _ = os.path.splitext(base_name)
# Now use the cleaned name for your MP3 file
mp3_name = f'{file_name_without_extension}_mp3'
support.convert_to_mp3(chunks, output_dir, name=mp3_name,
                   test_script=False)

# === MERGE ALL MP3 FILES ===
support.merge_mp3s(AudioSegment, mp3_name, output_dir=output_dir,clean_mp3s=False)

