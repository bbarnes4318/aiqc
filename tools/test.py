# Install dependencies
!pip install torch torchaudio openai-whisper requests

# Import libraries
import os
import whisper
import logging
import requests
from google.colab import drive

# Mount Google Drive (if using Colab)
drive.mount('/content/drive')

# Set up logging
logging.basicConfig(level=logging.INFO)

# Paths
AUDIO_FOLDER = "audio_files"  # Folder to store downloaded audio
os.makedirs(AUDIO_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist

# Whisper model initialization
model = whisper.load_model("base")  # Use "base" or "small" for better accuracy

# Deepseek API key
DEEPSEEK_API_KEY = "sk-b6cb01ef53944653b02acf26ad78b61f"  # Replace with your API key

# Function to test Deepseek API with a simple prompt
def test_deepseek_api():
    """
    Tests the Deepseek API with a simple prompt.
    """
    prompt = "Hello, how are you?"  # Simple fucking prompt
    try:
        headers = {
            "Authorization": f"Bearer sk-b6cb01ef53944653b02acf26ad78b61f",  # Replace with your API key
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",  # Specify the model
            "messages": [
                {
                    "role": "user",
                    "content": prompt  # Your simple prompt
                }
            ],
            "temperature": 0.5,  # Adjust as needed
            "max_tokens": 50  # Limit the response length for testing
        }
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30  # 30-second timeout
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        logging.error("Deepseek API request timed out.")
        return "Test failed: API request timed out."
    except requests.exceptions.HTTPError as e:
        logging.error(f"Deepseek API request failed: {e}")
        logging.error(f"Response: {response.text}")  # Log the API response for debugging
        return "Test failed: API request failed."
    except Exception as e:
        logging.error(f"Test failed: {e}")
        return "Test failed."

# Function to read URLs from file
def read_urls_from_file(file_name='/content/drive/MyDrive/urls3.txt'):
    """Reads URLs from a file and returns a list of URLs."""
    if not os.path.exists(file_name):
        logging.error(f"File not found: {file_name}")
        return []
    with open(file_name, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls if url.strip()]

# Function to download audio
def download_audio(url, output_folder):
    """Downloads an MP3 file from the given URL and saves it in the specified folder."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    audio_file_name = os.path.join(output_folder, os.path.basename(url.split('?')[0]) + ".mp3")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(audio_file_name, 'wb') as f:
            f.write(response.content)
        logging.info(f"Downloaded audio to {audio_file_name}")
    except requests.RequestException as e:
        logging.error(f"Failed to download audio: {e}")
        return None
    return audio_file_name

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

# Function to analyze transcript with Deepseek
def analyze_transcript_with_llm(transcript):
    """
    Sends the generated prompt to Deepseek's API for analysis.
    """
    prompt = f"""
    Analyze the following call transcript:
    {transcript}

    [Your analysis instructions here...]
    """
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",  # Specify the model
            "messages": [
                {
                    "role": "user",
                    "content": prompt  # Your prompt goes here
                }
            ],
            "temperature": 0.5,  # Adjust as needed
            "max_tokens": 750  # Adjust as needed
        }
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30  # 30-second timeout
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        logging.error("Deepseek API request timed out.")
        return "Analysis failed: API request timed out."
    except requests.exceptions.HTTPError as e:
        logging.error(f"Deepseek API request failed: {e}")
        logging.error(f"Response: {response.text}")  # Log the API response for debugging
        return "Analysis failed: API request failed."
    except Exception as e:
        logging.error(f"Deepseek analysis failed: {e}")
        return "Analysis failed."

# Function to process a single call
def process_call(url, output_folder):
    """Processes a single call: download, transcribe, analyze, and save results."""
    audio_file_name = download_audio(url, output_folder)
    if not audio_file_name:
        logging.error(f"Failed to download audio for URL: {url}")
        return None

    try:
        # Transcribe audio
        logging.info("Starting transcription...")
        transcript = transcribe_audio(audio_file_name)
        if transcript:
            logging.info("Transcription completed. Starting analysis...")
            analysis_result = analyze_transcript_with_llm(transcript)
            logging.info(f"Analysis Result for {audio_file_name}:\n{analysis_result}")
        else:
            logging.error("No transcript generated.")
        return analysis_result
    except Exception as e:
        logging.error(f"Processing failed: {e}")
        return None
    finally:
        # Clean up downloaded audio
        if os.path.exists(audio_file_name):
            os.remove(audio_file_name)

# Function to process all calls
def process_all_calls():
    """Processes all calls from the URLs in the 'urls3.txt' file."""
    urls = read_urls_from_file()
    if not urls:
        logging.error("No URLs to process.")
        return

    for url in urls:
        logging.info(f"Processing: {url}")
        transcript = process_call(url, AUDIO_FOLDER)
        if transcript:
            logging.info(f"Transcript Analysis:\n{transcript}")
        else:
            logging.error(f"Failed to process {url}")
        logging.info("---------------------------------------------------")

# Run the test
test_result = test_deepseek_api()
print("Test Result:", test_result)

# Run the script
if __name__ == "__main__":
    process_all_calls()