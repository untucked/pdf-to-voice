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
import tkinter as tk
from tkinter import filedialog
config = configparser.ConfigParser()
config.read('config.conf')
from pydub.utils import which

# local
import support

# Set paths BEFORE importing AudioSegment
ffmpeg_path = config.get('paths', 'ffmpeg_path', fallback=None)
if not ffmpeg_path or not ffmpeg_path.strip():
    raise ValueError("❌ 'ffmpeg_path' is missing from config.conf")
elif not os.path.isfile(ffmpeg_path):
    raise FileNotFoundError(f"❌ ffmpeg_path is set to '{ffmpeg_path}', but that file does not exist.")


ffprobe_path = config.get('paths', 'ffmpeg_probe', fallback=None)
if not ffprobe_path or not ffprobe_path.strip():
    raise ValueError("❌ 'ffmpeg_probe' is missing from config.conf")
elif not os.path.isfile(ffprobe_path):
    raise FileNotFoundError(f"❌ ffmpeg_probe is set to '{ffprobe_path}', but that file does not exist.")


AudioSegment.converter = which(ffmpeg_path)

os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)  # Add to PATH at runtime

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

test_load_pdf = False
# === CONFIG ===
if test_load_pdf:
    pdf_path = config.get('read', 'read_essay', fallback='Tell-Tale_Heart.pdf')
else:
    # Prompt user to choose a file via GUI
    root = tk.Tk()
    root.withdraw()  # Hide the empty Tkinter window
    pdf_path = filedialog.askopenfilename(
        title="Select a PDF to read",
        filetypes=[("PDF files", "*.pdf")],
    )

    if not pdf_path:
        raise ValueError("No file selected — exiting.")

    print(f"📄 Selected file: {pdf_path}")
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

