# PDF to Voice
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25.0-blue.svg)

## 🎧 Introduction
This tool converts PDF files into spoken audio (MP3). It handles both:
- **Text-based PDFs** using `pdfplumber`
- **Image-based PDFs** (like scanned documents) using **OCR** with `Tesseract` + `Poppler`.

Why? Because I don’t want to pay for Adobe’s read-aloud tools — and now I don’t need to.

---

## 🎯 Goal
- Convert any PDF (text or scanned image) to MP3 audio
- Automatically detect if OCR is needed and fall back to it
- Create chunked audio files and merge them with part intros
- Save timestamps for easy reference
- Make it easy to listen to essays, reports, or long documents while on the go

---

## ⚙️ How It Works
1. **PDF Detection**: Checks the first 3 pages to see if it's a scanned image (no extractable text).
2. **Extraction**:
   - Uses `pdfplumber` for regular text PDFs.
   - Falls back to `pytesseract` + `pdf2image` for image-based PDFs.
3. **Audio Conversion**:
   - Breaks text into chunks (~4900 characters).
   - Converts each chunk to MP3 using `gTTS`.
   - Prepends a short “Part X” intro for navigation.
4. **Merging**:
   - Combines all MP3 parts into one audio file with pauses.
   - Generates a `timestamps.txt` for reference.

---

## ✨ Features
- ✅ Automatic text vs image PDF detection
- 🎙️ Converts to MP3 with part intros and pauses
- 📑 Saves timestamps for audio indexing
- 🧠 Handles long PDFs with chunking
- 💡 Simple config via `config.conf`
- 📦 Clean modular code using `support.py`

---

## Dependencies 
----------------------------

ffmpeg & ffprobe:
https://www.gyan.dev/ffmpeg/builds/
https://github.com/Purple-CSGO/ffmpeg-gyan-git-builds/releases

tesseract:
https://github.com/tesseract-ocr/tesseract
download: https://github.com/UB-Mannheim/tesseract/wiki

Poppler:
https://github.com/oschwartz10612/poppler-windows/releases/

## GIT - CLONE
----------------------------
``` bash
git clone https://github.com/untucked/pdf-to-voice.git
```

#### GIT - Upload
----------------------------
``` bash
git init
git add .
git commit -m "Initialize"
git branch -M main
git remote add origin https://github.com/untucked/pdf-to-voice.git
git push -u origin main
```
