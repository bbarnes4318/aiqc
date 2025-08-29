# Import libraries
import os
import whisper
import logging
from pytube import YouTube
from yt_dlp import YoutubeDL

# Set up logging
logging.basicConfig(level=logging.INFO)

# Paths
AUDIO_FOLDER = "audio_files"  # Folder to store downloaded audio
os.makedirs(AUDIO_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist

# Whisper model initialization
model = whisper.load_model("base")  # Use "base" or "small" for better accuracy

# Function to read URLs from file
def read_urls_from_file(file_name='urls3.txt'):
    """Reads URLs from a file and returns a list of URLs."""
    if not os.path.exists(file_name):
        logging.error(f"File not found: {file_name}")
        return []
    with open(file_name, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls if url.strip()]

# Function to download audio from YouTube
def download_audio_from_youtube(url, output_folder):
    """Downloads audio from a YouTube video and saves it as an MP3 file."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        # Set options for yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',  # Download the best quality audio
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),  # Save file with the video title
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',  # Extract audio
                'preferredcodec': 'mp3',      # Convert to MP3
                'preferredquality': '192',    # Set audio quality
            }],
            'quiet': True,  # Suppress yt-dlp output
        }

        # Download the audio
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            audio_file_name = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
        
        logging.info(f"Downloaded audio to {audio_file_name}")
        return audio_file_name
    except Exception as e:
        logging.error(f"Failed to download audio from YouTube: {e}")
        return None

# Function to transcribe audio
def transcribe_audio(file_path):
    """Transcribes audio using Whisper."""
    logging.info(f"Transcribing audio: {file_path}")
    try:
        result = model.transcribe(file_path)
        return result.get("text", "")
    except Exception as e:
        logging.error(f"Transcription failed for {file_path}: {e}")
        return ""

# Function to process all calls
def process_all_calls():
    """Processes all calls from the URLs in the 'urls3.txt' file."""
    urls = read_urls_from_file()
    if not urls:
        logging.error("No URLs to process.")
        return

    for url in urls:
        logging.info(f"Processing: {url}")
        audio_file_name = download_audio_from_youtube(url, AUDIO_FOLDER)
        if not audio_file_name:
            logging.error(f"Failed to download audio for URL: {url}")
            continue

        try:
            # Transcribe audio
            logging.info("Starting transcription...")
            transcript = transcribe_audio(audio_file_name)
            if transcript:
                # Save the transcription to a text file
                transcript_file_name = os.path.splitext(audio_file_name)[0] + ".txt"
                with open(transcript_file_name, 'w') as f:
                    f.write(transcript)
                logging.info(f"Transcription saved to {transcript_file_name}")
            else:
                logging.error("No transcript generated.")
        except Exception as e:
            logging.error(f"Processing failed: {e}")
        finally:
            # Clean up downloaded audio
            if os.path.exists(audio_file_name):
                os.remove(audio_file_name)
            logging.info(f"Finished processing for URL: {url}")
        logging.info("---------------------------------------------------")

# Run the script
if __name__ == "__main__":
    process_all_calls()