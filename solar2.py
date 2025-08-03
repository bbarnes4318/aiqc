from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Import libraries
import os
import whisper
import logging
import datetime # Added for date calculation
import re # Added for regex operations
import requests # Re-enabled for downloading from URLs
import hashlib # Re-enabled for filename hashing from URLs
from urllib.parse import urlparse, unquote # Re-enabled for URL parsing

# Attempt to import dateutil, warn if not found
try:
    from dateutil.relativedelta import relativedelta
    dateutil_available = True
except ImportError:
    dateutil_available = False

# Attempt to import pydub for audio conversion, warn if not found or ffmpeg is missing
try:
    from pydub import AudioSegment
    from pydub.exceptions import CouldntDecodeError
    pydub_available = True
except ImportError:
    pydub_available = False
    AudioSegment = None # Define for type hinting or checks
    CouldntDecodeError = None # Define for type hinting or checks
except FileNotFoundError: # This can happen if ffmpeg/avprobe is not found by pydub
    pydub_available = False
    AudioSegment = None
    CouldntDecodeError = None
    logging.warning("pydub loaded but ffmpeg/avprobe might be missing. Conversion from URL may fail.")


# Set up logging
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file = 'transcription_log.log'

# File Handler
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Get the logger
logger = logging.getLogger("TranscriptionApp")
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

# --- Configuration Constants ---
# Folder for local audio files provided by the user
LOCAL_AUDIO_FOLDER = "solar-recordings"
# File containing URLs to download
URL_FILE = "urls.txt"
# Parent folder for audio files downloaded from URLs
DOWNLOADED_AUDIO_PARENT_FOLDER = "downloaded_audio_files"
DOWNLOADED_ORIGINALS_FOLDER = os.path.join(DOWNLOADED_AUDIO_PARENT_FOLDER, "originals")
DOWNLOADED_CONVERTED_FOLDER = os.path.join(DOWNLOADED_AUDIO_PARENT_FOLDER, "converted_mp3")
# Folder to store analysis results
ANALYSIS_FOLDER = "analysis_results"
# Folder to store raw transcripts  <--- NEW
TRANSCRIPTS_FOLDER = "transcripts_output"


# Create necessary directories
os.makedirs(LOCAL_AUDIO_FOLDER, exist_ok=True) # For user's local files
os.makedirs(DOWNLOADED_ORIGINALS_FOLDER, exist_ok=True) # For raw downloaded files
os.makedirs(DOWNLOADED_CONVERTED_FOLDER, exist_ok=True) # For MP3 converted files from URLs
os.makedirs(ANALYSIS_FOLDER, exist_ok=True) # For analysis results
os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True) # For raw transcript files <--- NEW

# Whisper model initialization
try:
    model = whisper.load_model("base")
    logger.info("Whisper model 'base' loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {e}")
    logger.error("Ensure PyTorch is installed correctly for your system (CPU or GPU).")
    logger.error("If using GPU, check CUDA compatibility and drivers.")
    logger.error("Try installing the CPU-only version: pip install -U openai-whisper torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")
    logger.error("Also ensure ffmpeg is installed and in your system's PATH (required by Whisper and Pydub).")
    exit(1)

if not pydub_available:
    logger.warning("Pydub library is not available or its dependency (ffmpeg) is missing. "
                   "Processing audio from URLs will be skipped or may fail if conversion is needed.")
    logger.warning("To install pydub: pip install pydub")
    logger.warning("Ensure ffmpeg is installed and added to your system's PATH.")


# Deepseek API key - Hardcoded directly (Less secure)
DEEPSEEK_API_KEY = "sk-b6cb01ef53944653b02acf26ad78b61f" # Replace with your actual key or use environment variables

# Deepgram API key
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')  # Replace with your actual Deepgram API key

# --- Function Definitions ---

def read_audio_urls_from_file(file_path):
    """Reads a list of URLs from a text file (one URL per line)."""
    urls = []
    if not os.path.exists(file_path):
        logger.warning(f"URL file not found: {file_path}. Skipping URL processing.")
        return urls
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'): # Ignore empty lines and comments
                    urls.append(url)
        logger.info(f"Read {len(urls)} URLs from {file_path}")
    except Exception as e:
        logger.error(f"Error reading URL file {file_path}: {e}")
    return urls

def generate_safe_filename_from_url(url):
    """Generates a safe filename base from a URL and tries to get an extension."""
    parsed_url = urlparse(url)
    # Use a hash of the path and query for uniqueness if path is generic
    name_base = os.path.splitext(unquote(os.path.basename(parsed_url.path)))[0]
    if not name_base or len(name_base) < 5 : # if path is like '/' or very short
        name_base = hashlib.md5(url.encode('utf-8')).hexdigest()[:16]

    # Attempt to get extension from path
    _, ext = os.path.splitext(unquote(os.path.basename(parsed_url.path)))
    if not ext or len(ext) > 5: # if no ext or very long ext (likely not a real ext)
        ext = ".bin" # default if no clear extension

    return f"{name_base[:100]}{ext}" # Truncate base name if too long

def download_and_convert_audio(url, original_folder, converted_folder):
    """Downloads audio from a URL, saves it, and converts it to MP3."""
    if not pydub_available or AudioSegment is None:
        logger.error(f"Pydub not available. Cannot download and convert URL: {url}")
        return None

    try:
        logger.info(f"Attempting to download: {url}")
        response = requests.get(url, stream=True, timeout=60) # Increased timeout for large files
        response.raise_for_status()

        original_filename_base = generate_safe_filename_from_url(url)
        original_filepath = os.path.join(original_folder, original_filename_base)

        with open(original_filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Successfully downloaded to: {original_filepath}")

        # Convert to MP3
        mp3_filename = os.path.splitext(os.path.basename(original_filepath))[0] + ".mp3"
        mp3_filepath = os.path.join(converted_folder, mp3_filename)

        logger.info(f"Attempting to convert {original_filepath} to MP3...")
        try:
            audio = AudioSegment.from_file(original_filepath) # Pydub attempts to infer format
            audio.export(mp3_filepath, format="mp3")
            logger.info(f"Successfully converted and saved to: {mp3_filepath}")
            # Optionally, remove the original downloaded file after conversion
            # try:
            # os.remove(original_filepath)
            #     logger.debug(f"Removed original downloaded file: {original_filepath}")
            # except OSError as e:
            #     logger.warning(f"Could not remove original downloaded file {original_filepath}: {e}")
            return mp3_filepath
        except CouldntDecodeError as cde:
            logger.error(f"Pydub CouldntDecodeError for {original_filepath}: {cde}. "
                         "The file might not be a valid audio format or ffmpeg had issues.")
            logger.error("Ensure the URL points to a direct audio file or a format ffmpeg can handle.")
            return None
        except Exception as e_conv:
            logger.error(f"Failed to convert {original_filepath} to MP3: {e_conv}")
            return None

    except requests.exceptions.RequestException as e_req:
        logger.error(f"Failed to download {url}: {e_req}")
        return None
    except Exception as e_gen:
        logger.error(f"An unexpected error occurred during download/conversion of {url}: {e_gen}")
        return None


def list_local_audio_files(input_folder):
    """Lists MP3 and WAV files in the specified input folder."""
    if not os.path.isdir(input_folder):
        logger.warning(f"Local audio folder not found or is not a directory: {input_folder}")
        return []
    try:
        files = [f for f in os.listdir(input_folder)
                 if os.path.isfile(os.path.join(input_folder, f)) and
                    (f.lower().endswith('.mp3') or f.lower().endswith('.wav'))]
        logger.info(f"Found {len(files)} MP3/WAV files in {input_folder}")
        return files
    except Exception as e:
        logger.exception(f"Error listing files in {input_folder}: {e}")
        return []


def transcribe_audio_deepgram(file_path):
    """Transcribes audio using the Deepgram API."""
    if not os.path.exists(file_path):
        logger.error(f"Audio file not found for Deepgram transcription: {file_path}")
        return ""
    try:
        if os.path.getsize(file_path) == 0:
            logger.error(f"Audio file is empty, skipping Deepgram transcription: {file_path}")
            return ""
    except OSError as e:
        logger.error(f"Could not get file size for {file_path}: {e}. Skipping Deepgram transcription.")
        return ""

    logger.info(f"Starting Deepgram transcription for: {file_path}")
    url = "https://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
    }
    try:
        with open(file_path, "rb") as audio_file:
            response = requests.post(url, headers=headers, files={"file": audio_file})
        response.raise_for_status()
        result = response.json()
        transcript_text = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "").strip()
        if not transcript_text:
            logger.warning(f"Deepgram transcription resulted in empty text for: {file_path}. Check audio content.")
        else:
            logger.info(f"Deepgram transcription successful for: {file_path}")
            logger.debug(f"Deepgram transcript snippet: {transcript_text[:150]}...")
        return transcript_text
    except Exception as e:
        logger.exception(f"Deepgram transcription failed for {file_path}: {e}")
        return ""

def transcribe_audio(file_path, engine="whisper"):
    """Transcribes audio using the selected engine ('whisper' or 'deepgram')."""
    if engine == "deepgram":
        return transcribe_audio_deepgram(file_path)
    # Default: Whisper
    if not os.path.exists(file_path):
        logger.error(f"Audio file not found for transcription: {file_path}")
        return ""
    try:
        if os.path.getsize(file_path) == 0:
            logger.error(f"Audio file is empty, skipping transcription: {file_path}")
            return ""
    except OSError as e:
        logger.error(f"Could not get file size for {file_path}: {e}. Skipping transcription.")
        return ""

    logger.info(f"Starting transcription for: {file_path}")
    try:
        result = model.transcribe(file_path, fp16=False) # Consider fp16=True if using GPU
        transcript_text = result.get("text", "").strip()
        if not transcript_text:
            logger.warning(f"Transcription resulted in empty text for: {file_path}. Check audio content.")
        else:
            logger.info(f"Transcription successful for: {file_path}")
            logger.debug(f"Transcript snippet: {transcript_text[:150]}...")
        return transcript_text
    except Exception as e:
        logger.exception(f"Whisper transcription failed for {file_path}: {e}")
        if "ffmpeg" in str(e).lower():
            logger.error("This might be an issue with the ffmpeg installation or the audio file format/integrity.")
            logger.error("Ensure ffmpeg is installed and in your system's PATH.")
        if "cuda" in str(e).lower() or "cublas" in str(e).lower():
            logger.error("A CUDA-related error occurred. Check GPU memory, drivers, and PyTorch/CUDA compatibility.")
        if "memory" in str(e).lower():
            logger.error("An out-of-memory error occurred. Try a smaller Whisper model or process shorter audio segments if possible.")
        return ""

def analyze_transcript_with_llm(transcript, audio_filename):
    """Sends the transcript to Deepseek's API for analysis."""
    if not transcript:
        logger.warning(f"Skipping analysis for {audio_filename} due to empty transcript.")
        return "Analysis skipped: Empty transcript provided."
    if not DEEPSEEK_API_KEY or "YOUR_DEFAULT_KEY_HERE" in DEEPSEEK_API_KEY or len(DEEPSEEK_API_KEY) < 10:
        logger.error("Deepseek API key is not configured correctly or is invalid. Skipping analysis.")
        return "Analysis failed: Deepseek API key not set or invalid."

    logger.info(f"Sending transcript for analysis: {audio_filename} (length: {len(transcript)} chars)")
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # today = datetime.date.today() # Commented out as it's not used in the provided prompt for LLM
        # cutoff_date_str = "April 24, 1944" # Default fallback
        # if dateutil_available:
        #     try:
        #         cutoff_date = today - relativedelta(years=81)
        #         cutoff_date_str = cutoff_date.strftime("%B %d, %Y")
        #         logger.info(f"Using age cutoff date (81+): Born on or before {cutoff_date_str}")
        #     except Exception as date_err:
        #         logger.error(f"Error calculating cutoff date using dateutil: {date_err}. Using fixed placeholder.")
        # else:
        #     logger.warning("python-dateutil library not found. Using approximate age cutoff calculation.")
        #     cutoff_year = today.year - 81
        #     cutoff_date_str = f"approximately before {today.strftime('%B %d')}, {cutoff_year}"

        prompt_content = f"""
Analyze the following call transcript:
--- TRANSCRIPT START ---
{transcript}
--- TRANSCRIPT END ---

Your Objectives:

# AI Prompt for Evaluating Solar Call Transcripts

You are an expert AI assistant assigned to evaluate call recording transcripts based on specific criteria for determining if a prospect qualifies as a "callback lead" for a solar savings program. Please follow the instructions below to analyze the transcript and extract the required information. Be thorough and concise in your evaluation.

---

## Instructions

### 1. Evaluate the Transcript for Callback Lead Qualification

Determine if the prospect meets the callback lead criteria based on the following requirements:
- **Homeowner Status**: Confirm if the prospect is a homeowner.
- **Electric Bill Amount**: Confirm if the prospect's electric bill is $100 or more per month.
**Important**: If any of these **two criteria** are NOT met, mark the prospect as **"Not Qualified for Callback Lead."**

---

### 2. Extract Key Information
Identify and extract the following details from the transcript. The following do not have any bearing on whether the call is qualified or not. These are for information purposes only:
- **Contact Information**: Confirm if the prospect's first name and last name are provided are provide the first name and last name.
- **Credit Score**: Confirm if the prospect agrees that their credit score is 600 or above, or uses similar wording to indicate fair or decent credit.
- **Roof Sunlight Exposure**: Confirm if the prospect agrees that their roof gets good sunlight exposure with no major shade or obstructions.
- Prospect's **First Name** and **Last Name**
- Prospect's **Phone Number**
- **Transfer Outcome**: Did the agent successfully transfer the prospect to a solar specialist? (Yes/No)
- If **No Transfer**: Did the agent inform the prospect that they will receive a callback? (Yes/No)
- Did the prospect say that they were not interested in speaking to someone about solar? (Yes/No)
- Did the prospect say that they don't know their zip code? (Yes/No)

---

### 3. Response Format
Provide your response in the following format:

**Callback Lead Qualification**: [Qualified/Not Qualified]

**Reason for Disqualification (if applicable)**: [Specify which criteria were not met.]

**Extracted Information**:
- First Name: [Insert Prospect's First Name]
- Last Name: [Insert Prospect's Last Name]
- Credit Score: Confirm if the prospect agrees that their credit score is 600 or above [Yes/No]
- Roof Sunlight Exposure: Confirm if the prospect agrees that their roof gets good sunlight exposure with no major shade or obstructions [Yes/No]
- Phone Number: [Insert Prospect's Phone Number]
- Was the Prospect Transferred to a Solar Specialist?: [Yes/No]
- If No Transfer, Did the Agent Inform the Prospect About a Callback?: [Yes/No]
- Did the prospect say that they were not interested in speaking to someone about solar? (Yes/No)
- Did the prospect say that they don't know their zip code? (Yes/No)

4. Provide Justifications
If the prospect is Not Qualified, explain why. For example:
"Prospect stated their electric bill is under $100 per month."
"Credit score information was not provided."

Example Transcript Evaluation

Transcript Example
Agent: Hi! This is John calling from Solar USA — how are you today?
Prospect: I'm good, thank you.
Agent: I'm reaching out because it looks like your home might qualify for our solar savings program, which could help you reduce your electric bill by up to 50%. I just need to ask a few quick questions to confirm your eligibility — it won't take more than a minute!
Agent: You're the homeowner of a single-family house, correct?
Prospect: Yes, I am.
Agent: On average, would you say your electric bill is $100 per month or more?
Prospect:Yes,it'susually around $150.
Agent: Who's your electric utility provider?
Prospect: XYZ Energy.
Agent: Do you have a credit score above 600 and usually pay your bills on time?
Prospect: Yes, I think my credit is decent.
Agent: And your roof gets good sunlight exposure — no major shade or obstructions, right?
Prospect: Yes, it gets plenty of sun.
Agent: Great! Can I get your first and last name?
Prospect: Sure, it's Jane Smith.
Agent: And we're calling you at 555-123-4567, is that the best number for a callback?
Prospect: Yes, that's correct.
Agent: Perfect — based on your answers, it looks like you're a great fit! Let me go ahead and connect you right now with one of our solar specialists who can explain your options, answer your questions, and show you exactly how much you can save.
(Transfer attempt occurs, but no specialist is available.)
Agent: No problem — I've noted everything, and a solar expert will call you back in the next day or two. Thanks so much for your time — have a great day!


**Callback Lead Qualification**: Qualified

**Reason for Disqualification (if applicable)**: N/A

**Extracted Information**:
- First Name: Jane
- Last Name: Smith
- Credit Score: Yes
- Roof Sunlight Exposure: Yes
- Phone Number: 5551234567
- Was the Prospect Transferred to a Solar Specialist?: No
- If No Transfer, Did the Agent Inform the Prospect About a Callback?: Yes
- Did the prospect say that they were not interested in speaking to someone about solar? (Yes/No)
- Did the prospect say that they don't know their zip code? (Yes/No)
"""
        messages = [
            {"role": "system", "content": "You are an AI assistant analyzing call transcripts. Provide ONLY the requested structured data."},
            {"role": "user", "content": prompt_content}
        ]

        data = {
            "messages": messages,
            "model": "deepseek-chat",
            "max_tokens": 1024,
            "temperature": 0.1,
            "stream": False,
        }

        api_endpoint = "https://api.deepseek.com/v1/chat/completions"

        logger.debug(f"Sending request to Deepseek API. Endpoint: {api_endpoint}")
        response = requests.post(api_endpoint, headers=headers, json=data, timeout=90)
        logger.debug(f"Received response from Deepseek API. Status code: {response.status_code}")
        response.raise_for_status()

        result = response.json()
        logger.debug(f"Deepseek API Response (usage): {result.get('usage')}")
        if "choices" in result and len(result["choices"]) > 0:
            logger.debug(f"Deepseek API Response (finish_reason): {result['choices'][0].get('finish_reason')}")

        if "choices" in result and len(result["choices"]) > 0 and "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
            analysis_content = result["choices"][0]["message"]["content"].strip()
            if not analysis_content.startswith(("Callback Lead Qualification:", "**Callback Lead Qualification**:")):
                logger.warning(f"Analysis output for {audio_filename} does not start as expected. Content: {analysis_content[:100]}...")
            else:
                logger.info(f"Analysis successful for: {audio_filename}")
            return analysis_content
        else:
            logger.error(f"Deepseek API response format unexpected or empty for {audio_filename}. Raw Response: {result}")
            return "Analysis failed: Unexpected API response format."

    except requests.exceptions.Timeout:
        logger.error(f"Deepseek API request timed out for {audio_filename}")
        return "Analysis failed: API request timed out"
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred during Deepseek API call for {audio_filename}: {http_err}")
        error_message = f"Analysis failed: API Error {response.status_code}."
        try:
            error_details = response.json()
            logger.error(f"API Error Details: {error_details}")
            api_msg = error_details.get('error', {}).get('message', '')
            if api_msg: error_message += f" Message: {api_msg}"
            else: error_message += f" Response: {response.text[:500]}"
        except requests.exceptions.JSONDecodeError:
            logger.error(f"API Response Text (non-JSON): {response.text[:500]}")
            error_message += f" Check API key, endpoint, model name, and request format. Response: {response.text[:200]}"
        return error_message
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception occurred during Deepseek API call for {audio_filename}: {req_err}")
        if isinstance(req_err, requests.exceptions.InvalidSchema):
            logger.error(f"InvalidSchema error: The URL '{api_endpoint}' is likely malformed.")
        return f"Analysis failed: Network or connection error ({type(req_err).__name__})"
    except Exception as e:
        logger.exception(f"An unexpected error occurred during LLM analysis for {audio_filename}: {e}")
        return f"Analysis failed: Unexpected error ({type(e).__name__})"

def save_transcript_to_file(transcript_text, base_filename, transcript_folder_path): # <--- NEW FUNCTION
    """Saves the transcript text to a file."""
    try:
        transcript_filename = f"{os.path.splitext(base_filename)[0]}_transcript.txt"
        transcript_filepath = os.path.join(transcript_folder_path, transcript_filename)

        with open(transcript_filepath, 'w', encoding='utf-8') as f:
            f.write(transcript_text)
        logger.info(f"Transcript saved to: {transcript_filepath}")
        return True
    except Exception as e:
        logger.exception(f"Failed to save transcript file for {base_filename}: {e}")
        return False

def save_analysis_to_file(analysis_content, base_filename, analysis_folder_path):
    """Saves the analysis content to a text file."""
    try:
        analysis_filename = f"{os.path.splitext(base_filename)[0]}_analysis.txt"
        analysis_filepath = os.path.join(analysis_folder_path, analysis_filename)

        with open(analysis_filepath, 'w', encoding='utf-8') as f:
            f.write(analysis_content)
        logger.info(f"Analysis saved to: {analysis_filepath}")
        return True
    except Exception as e:
        logger.exception(f"Failed to save analysis file for {base_filename}: {e}")
        return False

def process_single_audio_file(audio_file_path, current_transcripts_folder, current_analysis_folder, engine="whisper"):
    """Transcribes, saves transcript, analyzes, and saves analysis for a single audio file."""
    logger.info(f"Processing File: {audio_file_path}")
    analysis_result = "Analysis not performed"
    transcript = ""
    status = "Started"
    audio_filename = os.path.basename(audio_file_path)
    transcript_saved = False # <--- NEW

    try:
        # 1. Transcribe
        transcript = transcribe_audio(audio_file_path, engine=engine)
        if not transcript:
            logger.error(f"Transcription failed or resulted in empty text for {audio_filename}. Skipping further processing.")
            analysis_result = "Analysis skipped: Transcription failed or empty"
            status = "Transcription Failed"
        else:
            status = "Transcribed"
            # 1.1 Save Transcript <--- NEW
            if save_transcript_to_file(transcript, audio_filename, current_transcripts_folder):
                transcript_saved = True
                status = "Transcript Saved" # Update status or add another status for summary
            else:
                logger.error(f"Failed to save transcript for {audio_filename}. Analysis will still proceed if possible.")
                # Optionally change status here if saving transcript is critical
                status = "Save Transcript Failed"


            # 2. Analyze (only if transcript exists)
            analysis_result = analyze_transcript_with_llm(transcript, audio_filename)
            if "Analysis failed" in analysis_result:
                status = "Analysis Failed"
                logger.error(f"Analysis failed for {audio_filename}: {analysis_result}")
            elif "Analysis skipped" in analysis_result: # Should only happen if transcript was technically empty but not from transcribe_audio error
                status = "Analysis Skipped"
                logger.warning(f"Analysis skipped for {audio_filename}.")
            else:
                # 3. Save Analysis to File (only on successful analysis)
                if save_analysis_to_file(analysis_result, audio_filename, current_analysis_folder):
                    status = "Analysis Success" # This implies transcript was also available
                else:
                    status = "Save Analysis Failed"
                    logger.error(f"Failed to save analysis file, logging result for {audio_filename} here:\n{analysis_result}")

    except Exception as e:
        logger.exception(f"A critical unexpected error occurred processing file {audio_filename}: {e}")
        analysis_result = f"Analysis failed: Critical error during processing ({type(e).__name__})"
        logger.error(analysis_result) # Log the error message itself
        status = "Critical Error"
    finally:
        # Refine final status based on transcript save outcome if desired
        if status == "Transcribed" and not transcript_saved: # If only transcription happened, but saving it failed
             pass # Keep status as is or use a more specific one
        elif status == "Analysis Success" and not transcript_saved:
            logger.warning(f"Analysis for {audio_filename} was successful, but saving the raw transcript failed earlier.")
            # Status remains "Analysis Success" for the analysis part, but transcript saving part failed.
            # You might want a more granular status in status_counts if this distinction is important.

        logger.info(f"Finished processing attempt for File: {audio_filename}. Final Status: {status}")
        logger.info("-" * 70)
        return status

# --- Main Script Execution ---
if __name__ == "__main__":
    logger.info("Script started. Log file: %s", log_file)
    if not dateutil_available:
        logger.warning("python-dateutil library not found (pip install python-dateutil). Age calculation will be approximate.")

    # Ensure analysis and transcript folders exist
    try:
        os.makedirs(ANALYSIS_FOLDER, exist_ok=True)
        os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True) # <--- Ensure transcript folder is checked/created
    except OSError as e:
        logger.error(f"Could not create output directories ('{ANALYSIS_FOLDER}', '{TRANSCRIPTS_FOLDER}'): {e}. Exiting.")
        exit(1)

    # --- Collect all audio file paths ---
    all_audio_file_paths = []

    # 1. From local 'solar-recordings' folder
    logger.info(f"Checking for local audio files in: {LOCAL_AUDIO_FOLDER}")
    if not os.path.isdir(LOCAL_AUDIO_FOLDER):
        logger.warning(f"Local audio folder '{LOCAL_AUDIO_FOLDER}' not found. Creating it. Please add audio files there if needed.")
        try:
            os.makedirs(LOCAL_AUDIO_FOLDER, exist_ok=True)
        except OSError as e:
            logger.error(f"Could not create local audio directory '{LOCAL_AUDIO_FOLDER}': {e}. Please create it manually.")
    else:
        local_files = list_local_audio_files(LOCAL_AUDIO_FOLDER)
        for lf in local_files:
            all_audio_file_paths.append(os.path.join(LOCAL_AUDIO_FOLDER, lf))

    # 2. From 'urls.txt'
    logger.info(f"Checking for audio URLs in: {URL_FILE}")
    audio_urls = read_audio_urls_from_file(URL_FILE)
    if audio_urls:
        if not pydub_available:
            logger.error("Pydub or ffmpeg is not available. Cannot process URLs that require conversion. Skipping URL downloads.")
        else:
            logger.info(f"Found {len(audio_urls)} URLs. Attempting to download and convert...")
            for i, url in enumerate(audio_urls, 1):
                logger.info(f"--- Downloading and Converting URL {i}/{len(audio_urls)}: {url} ---")
                downloaded_and_converted_path = download_and_convert_audio(url, DOWNLOADED_ORIGINALS_FOLDER, DOWNLOADED_CONVERTED_FOLDER)
                if downloaded_and_converted_path:
                    all_audio_file_paths.append(downloaded_and_converted_path)
                else:
                    logger.error(f"Failed to download or convert URL: {url}")
                    # Consider adding a specific status for download/conversion failures if needed for summary
    else:
        logger.info("No URLs found in 'urls.txt' or file does not exist.")


    # --- Process all collected audio files ---
    if not all_audio_file_paths:
        logger.warning("No audio files found from local folder or URLs. Exiting.")
        exit(0)

    total_files_to_process = len(all_audio_file_paths)
    logger.info(f"Starting processing for {total_files_to_process} audio files...")
    logger.info(f"Raw transcripts will be saved in: {os.path.abspath(TRANSCRIPTS_FOLDER)}") # <--- Log transcript folder
    logger.info(f"Analysis results will be saved in: {os.path.abspath(ANALYSIS_FOLDER)}")


    status_counts = {
        "Analysis Success": 0, # Implies transcript was generated and saved, and analysis saved
        "Transcript Saved": 0, # If analysis fails but transcript was saved
        "Save Transcript Failed": 0, # If transcript generation worked but saving failed
        "Download/Convert Failed": 0, # For URL specific issues before transcription
        "Transcription Failed": 0, # No transcript, no analysis
        "Analysis Failed": 0, # Transcript generated (and hopefully saved), but LLM analysis failed
        "Analysis Skipped": 0, # Transcript was empty
        "Save Analysis Failed": 0, # Analysis done, but saving analysis file failed
        "Critical Error": 0,
        "Started": 0, # Should not be a final state
        "Unknown": 0
    }


    for i, file_path in enumerate(all_audio_file_paths, 1):
        logger.info(f"--- Processing collected audio file {i}/{total_files_to_process}: {file_path} ---")
        final_status = "Unknown"
        try:
            # Pass both folder paths to the processing function
            # Now using Deepgram as the default engine
            final_status = process_single_audio_file(file_path, TRANSCRIPTS_FOLDER, ANALYSIS_FOLDER, engine="deepgram")
        except Exception as loop_err:
            logger.error(f"A critical error occurred in the main processing loop for file {os.path.basename(file_path)}, attempting to continue: {loop_err}")
            final_status = "Critical Error"
        status_counts[final_status] = status_counts.get(final_status, 0) + 1

    # Log Summary Report
    logger.info("=" * 70)
    logger.info("Processing Summary:")
    logger.info(f"Total Audio Sources Located (Local + URLs successfully downloaded/converted): {total_files_to_process}")

    for status, count in status_counts.items():
        if count > 0:
            logger.info(f"- {status}: {count}")
    logger.info(f"Raw transcripts saved in: {os.path.abspath(TRANSCRIPTS_FOLDER)}") # <--- Log transcript folder
    logger.info(f"Analysis results saved in: {os.path.abspath(ANALYSIS_FOLDER)}")
    if pydub_available:
        logger.info(f"Downloaded original files (if any from URLs) are in: {os.path.abspath(DOWNLOADED_ORIGINALS_FOLDER)}")
        logger.info(f"Converted MP3 files (if any from URLs) are in: {os.path.abspath(DOWNLOADED_CONVERTED_FOLDER)}")
    logger.info("=" * 70)
    logger.info("Script finished.")