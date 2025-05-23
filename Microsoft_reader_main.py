import pdfplumber
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Optional: Set voice properties
engine.setProperty('rate', 200)  # Speed of speech
engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

# Load and read PDF
pdf_path = r'C:\Users\bradley.eylander\OneDrive - LMI Consulting\Documents\Personal\equity\Alpha Metallurgical Resources (AMR) – Comprehensive Investment Analysis.pdf'

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages):
        
        text = page.extract_text()
        if text:       
            engine.say(f"Reading page {page_num + 1}")
            engine.runAndWait()  # wait for that to finish before proceeding
            print(f"Reading page {page_num + 1}")
            engine.say(text)
            engine.runAndWait()
