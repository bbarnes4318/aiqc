import requests
import os
import time
import csv
import logging
import whisper
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# ================ CONFIGURATION ================
OUTPUT_DIR = "C:\\Users\\Jimbo\\Desktop\\vapi-pull"
CSV_FILE_PATH = "C:\\Users\\Jimbo\\Desktop\\trans_only.csv"
# ===============================================

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Set up logging
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WhisperTranscriber")
logger.setLevel(logging.INFO)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# Initialize Whisper model
try:
    model = whisper.load_model("base")
    logger.info("Whisper model 'base' loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {e}")
    exit(1)

os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_urls(file_name='urls.txt'):
    with open(file_name, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def download_audio(url, output_path):
    try:
        response = requests.get(url, stream=True, verify=False)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Downloaded: {output_path} ({os.path.getsize(output_path)} bytes)")
        return True
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        return False

def transcribe_audio(file_path):
    """Transcribes audio using the loaded Whisper model."""
    if not file_path or not os.path.exists(file_path):
        logger.error(f"Audio file not found: {file_path}")
        return ""
    
    try:
        result = model.transcribe(file_path, fp16=False)
        return result.get("text", "").strip()
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        return ""

def save_to_csv(url, text):
    try:
        file_exists = os.path.exists(CSV_FILE_PATH)
        with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['URL', 'Transcription'])
            writer.writerow([url, text])
        logger.info(f"Saved transcription for {url}")
    except Exception as e:
        logger.error(f"CSV save error: {str(e)}")

def process_urls():
    urls = read_urls()
    for url in urls:
        logger.info(f"\nProcessing: {url}")
        audio_file = os.path.join(OUTPUT_DIR, f"audio_{int(time.time())}.wav")
        
        if not download_audio(url, audio_file):
            continue
            
        # Transcribe directly using Whisper
        transcription = transcribe_audio(audio_file)
        if transcription:
            save_to_csv(url, transcription)
            
        try:
            os.remove(audio_file)
            logger.info(f"Cleaned up audio file: {audio_file}")
        except Exception as e:
            logger.error(f"Error removing audio file: {str(e)}")

if __name__ == "__main__":
    process_urls()
    logger.info(f"\nDone! Results saved to: {CSV_FILE_PATH}")