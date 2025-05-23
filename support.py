import re
import pdfplumber
from gtts import gTTS
import os
import time
from datetime import timedelta
import pytesseract
from pdf2image import convert_from_path

import configparser
import sys



def clean_text(text):
    # Remove bracketed [1], parenthetical (12)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\(\d+\)', '', text)
    # Remove sequences like "word 1 ." or "2 ," etc.
    text = re.sub(r'\b\d{1,3}\s+[.,](?=\s)', '', text)
    text = re.sub(r'(?<=[a-z])\s\d{1,2}\.(?=\s|$)', '', text)
    # Remove sequences like "25% 15 )."
    text = re.sub(r'(?<=\S)\s\d{1,3}\s*\)\.', '.', text)
    # Remove ref numbers after a valid year followed by `)` and more refs: "2024) 17 23"
    text = re.sub(r'((?:19|20)\d{2})\)\s+((?:\d{1,3}\s+)+)', r'\1 ', text)
    # Remove patterns like "2023 9 –" → "2023 –"
    text = re.sub(r'\b\d{1,3}(?=\s*[–-])', '', text)
    # Remove inline sequences like " 1 2 ." or "4\n5 ."
    text = re.sub(r'(?<=\s)(\d{1,3}(\s+|\n)+)+(?=[\.,\n])', '', text)
    # Collapse multiple spaces
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def init_pytesseract():
    config = configparser.ConfigParser()
    config.read('config.conf')

    tesseract_path = config.get('paths', 'tesseract_path', fallback=None)
    if not tesseract_path or not tesseract_path.strip():
        print('❌ Error: tesseract_path is not configured in the CONF file.', file=sys.stderr)
        raise ValueError('Need to configure tesseract_path in order to run this script.')

    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    poppler_bin = config.get('paths', 'poppler_bin', fallback=None)
    if not poppler_bin or not poppler_bin.strip():
        print('❌ Error: poppler_bin is not configured in the CONF file.', file=sys.stderr)
        raise ValueError('Need to configure poppler_bin in order to run this script.')

    return poppler_bin

def get_full_text_ocr(pdf_path):
    poppler_bin = init_pytesseract()
    full_text = ""

    try:
        pages = convert_from_path(pdf_path, poppler_path=poppler_bin, dpi=300)
    except Exception as e:
        raise RuntimeError(f"🚨 Failed to convert PDF to images: {e}")
    for i, page_image in enumerate(pages):
        print(f"Running OCR on page {i + 1}")
        text = pytesseract.image_to_string(page_image)
        if i==0:
            print(text)
        cleaned = clean_text(text)
        full_text += f"\n\n[Page {i + 1}]\n{cleaned}"
    return full_text

def get_full_text(pdf_path, print_text=False):    
    full_text = ""
    image_based_file=False
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        # determine if pdf is image based - if the first 2-5 pages are blank we know it's a picture based pdf and needs to be converted to text
        # Check only the first 3 pages for real text
        scanned_blank_pages = 0
        for page_num in range(min(3, len(pdf.pages))):
            page = pdf.pages[page_num]
            text = page.extract_text()
            if print_text:
                print(f"[Scan Check] Page {page_num + 1} text: {repr(text)}")
            if not text or not text.strip():
                scanned_blank_pages += 1

        if scanned_blank_pages == min(3, len(pdf.pages)):
            print("First 3 pages are blank – likely image-based PDF. Switching to OCR...")
            image_based_file = True
        else:
            print("Text found in first 3 pages moving forward with reading pdf")

        # OCR fallback if image-based
        if image_based_file:
            return get_full_text_ocr(pdf_path)
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if print_text:
                print(f"Page {page_num + 1} text: {repr(text)}")
            if text:
                print(f"Adding page {page_num + 1}")
                # print(text)
                cleaned_text = clean_text(text)
                # print(cleaned_text)
                full_text += f"\n\n[Page {page_num + 1}]\n{cleaned_text}"
    return full_text

def convert_to_mp3(chunks, output_dir, name='mp3_output',
                   test_script=False):
    for i, chunk in enumerate(chunks, 1):
        print(f"Generating MP3 part {i}/{len(chunks)}...")
        tts = gTTS(chunk, lang='en')
        # amr_analysis_part
        mp3_path = os.path.join(output_dir, f'{name}_part_{i}.mp3')
        tts.save(mp3_path)
        if test_script:
            if i > 1:
                break
    print(f"✅ Done! Saved {len(chunks)} MP3 files to:\n{output_dir}")


def merge_mp3s(AudioSegment, mp3_name, output_dir='output',
               audio_parts=False,
               clean_mp3s=False):
    print("🔊 Merging all MP3s into one file...")

    merged_audio = AudioSegment.empty()
    pause = AudioSegment.silent(duration=1000)  # 1.0 seconds of silence

    # Ensure correct order by sorting
    mp3_files = sorted([f for f in os.listdir(output_dir) if f.startswith(mp3_name) and f.endswith(".mp3")])
    timestamps = []
    current_duration_ms = 0  # in milliseconds
    for i, filename in enumerate(mp3_files, 1):
        part_path = os.path.join(output_dir, filename)

        # === Generate "Part N" voice intro
        if audio_parts:
            part_intro_text = f"Part {i}"
            tts = gTTS(part_intro_text, lang='en')

            # Save to temporary file
            temp_intro_path = os.path.join(output_dir, f"intro_part_{i}.mp3")
            tts.save(temp_intro_path)
            if not os.path.exists(temp_intro_path):
                raise FileNotFoundError(f"❌ gTTS failed to create file: {temp_intro_path}")
            # Add a small delay (in seconds)        
            time.sleep(10)  # Try a 0.1-second delay
            intro_audio = AudioSegment.from_mp3(temp_intro_path)
            os.remove(temp_intro_path)  # Clean up after use

        # === Load the main part audio
        part_audio = AudioSegment.from_mp3(part_path)

        # === Record timestamp BEFORE adding this section
        timestamp_str = str(timedelta(milliseconds=current_duration_ms))
        timestamps.append(f"Part {i} - {timestamp_str}")

        # === Concatenate: [Part Intro] + [Pause] + [Part Audio] + [Pause]
        if audio_parts:
            merged_audio += intro_audio + pause + part_audio + pause
            current_duration_ms += len(intro_audio) + len(pause) + len(part_audio) + len(pause)
        else:
            merged_audio += part_audio + pause
            current_duration_ms = len(part_audio) + len(pause)

    # === Export final merged audio
    final_output = os.path.join(output_dir, f"{mp3_name}_full.mp3")
    merged_audio.export(final_output, format="mp3")
    
    if clean_mp3s:
        # Optional: clear old MP3 files
        for f in os.listdir(output_dir):
            if f.endswith('.mp3') and f!=f"{mp3_name}_full.mp3":
                os.remove(os.path.join(output_dir, f))

    # Save timestamps to file
    timestamp_file = os.path.join(output_dir, "timestamps.txt")
    with open(timestamp_file, 'w') as f:
        for line in timestamps:
            f.write(line + '\n')

    print(f"🕒 Timestamps saved to:\n{timestamp_file}")
    print(f"✅ Merged audio with intros saved to:\n{final_output}")