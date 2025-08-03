# Import libraries
import os
import whisper # Keep one import
import logging
# import requests # <<< MODIFIED: No longer needed for downloading
import datetime # Added for date calculation
import re # Added for regex operations
# import hashlib # <<< MODIFIED: No longer needed for filename hashing
# from urllib.parse import urlparse, unquote # <<< MODIFIED: No longer needed for URL parsing

# Attempt to import dateutil, warn if not found
try:
    from dateutil.relativedelta import relativedelta
    dateutil_available = True
except ImportError:
    dateutil_available = False

# Set up logging
# Configure logging to output to both console and a file
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Added logger name
log_file = 'transcription_log.log'

# File Handler
file_handler = logging.FileHandler(log_file, encoding='utf-8') # Specify encoding
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Get the logger
logger = logging.getLogger("TranscriptionApp")
logger.setLevel(logging.INFO)
# Prevent adding handlers multiple times if the script is re-run in some environments
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False # Prevent root logger from also handling messages

# <<< MODIFIED: Define the input folder for local audio files
INPUT_AUDIO_FOLDER = r"C:\Users\Jimbo\Documents\FE Python Transcription App\mp3" # Use raw string for Windows path
ANALYSIS_FOLDER = "analysis_results" # Folder to store analysis results
# AUDIO_FOLDER = "audio_files" # <<< MODIFIED: No longer needed for downloads
# os.makedirs(AUDIO_FOLDER, exist_ok=True) # <<< MODIFIED: No longer needed
os.makedirs(ANALYSIS_FOLDER, exist_ok=True) # Create the analysis folder

# Whisper model initialization
# Consider adding error handling for model loading
try:
    model = whisper.load_model("base")
    logger.info("Whisper model 'base' loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {e}")
    logger.error("Ensure PyTorch is installed correctly for your system (CPU or GPU).")
    logger.error("If using GPU, check CUDA compatibility and drivers.")
    logger.error("Try installing the CPU-only version: pip install -U openai-whisper torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")
    logger.error("Also ensure ffmpeg is installed and in your system's PATH.")
    exit(1) # Exit with a non-zero code to indicate error

# Deepseek API key - Hardcoded directly (Less secure)
# <<< NOTE: It's recommended to load sensitive keys from environment variables or a config file
DEEPSEEK_API_KEY = "sk-b6cb01ef53944653b02acf26ad78b61f"

# --- Function Definitions ---

# <<< MODIFIED: Removed read_urls_from_file function
# <<< MODIFIED: Removed download_audio function

def list_audio_files(input_folder):
    """Lists MP3 and WAV files in the specified input folder."""
    if not os.path.isdir(input_folder):
        logger.error(f"Input audio folder not found or is not a directory: {input_folder}")
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


def transcribe_audio(file_path):
    """Transcribes audio using the loaded Whisper model."""
    # <<< MODIFIED: Simplified check, assumes path is valid if function is called
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
        result = model.transcribe(file_path, fp16=False) # <<< NOTE: Consider fp16=True if using GPU and compatible hardware
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
    # <<< NOTE: This function remains largely the same, but ensure `requests` is imported if you use it here.
    # <<< MODIFIED: Added import for requests inside the function since it's only used here now
    import requests

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

        # --- Define the dynamic birth date cutoff (Keep this logic) ---
        today = datetime.date.today()
        cutoff_date_str = "April 24, 1944" # Default fallback
        if dateutil_available:
            try:
                cutoff_date = today - relativedelta(years=81)
                cutoff_date_str = cutoff_date.strftime("%B %d, %Y")
                logger.info(f"Using age cutoff date (81+): Born on or before {cutoff_date_str}")
            except Exception as date_err:
                logger.error(f"Error calculating cutoff date using dateutil: {date_err}. Using fixed placeholder.")
        else:
             logger.warning("python-dateutil library not found. Using approximate age cutoff calculation.")
             cutoff_year = today.year - 81
             cutoff_date_str = f"approximately before {today.strftime('%B %d')}, {cutoff_year}"

        # --- Updated Prompt (Keep this logic) ---
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

4. Provide Justifications
If the prospect is Not Qualified, explain why. For example:
"Prospect stated their electric bill is under $100 per month."
"Credit score information was not provided."

Example Transcript Evaluation

Transcript Example
Agent: Hi! This is John calling from Solar USA — how are you today?
Prospect: I’m good, thank you.
Agent: I’m reaching out because it looks like your home might qualify for our solar savings program, which could help you reduce your electric bill by up to 50%. I just need to ask a few quick questions to confirm your eligibility — it won’t take more than a minute!
Agent: You’re the homeowner of a single-family house, correct?
Prospect: Yes, I am.
Agent: On average, would you say your electric bill is $100 per month or more?
Prospect:Yes,it’susually around $150.
Agent: Who’s your electric utility provider?
Prospect: XYZ Energy.
Agent: Do you have a credit score above 600 and usually pay your bills on time?
Prospect: Yes, I think my credit is decent.
Agent: And your roof gets good sunlight exposure — no major shade or obstructions, right?
Prospect: Yes, it gets plenty of sun.
Agent: Great! Can I get your first and last name?
Prospect: Sure, it’s Jane Smith.
Agent: And we’re calling you at 555-123-4567, is that the best number for a callback?
Prospect: Yes, that’s correct.
Agent: Perfect — based on your answers, it looks like you’re a great fit! Let me go ahead and connect you right now with one of our solar specialists who can explain your options, answer your questions, and show you exactly how much you can save.
(Transfer attempt occurs, but no specialist is available.)
Agent: No problem — I’ve noted everything, and a solar expert will call you back in the next day or two. Thanks so much for your time — have a great day!


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
"""
        messages = [
            # System message can still be helpful for overall context
            {"role": "system", "content": "You are an AI assistant analyzing call transcripts. Provide ONLY the requested structured data."},
            {"role": "user", "content": prompt_content}
        ]

        data = {
            "messages": messages,
            "model": "deepseek-chat",
            "max_tokens": 1024, # Adjusted slightly, analysis output is structured and shorter now
            "temperature": 0.1,
            "stream": False,
        }

        api_endpoint = "https://api.deepseek.com/v1/chat/completions"

        logger.debug(f"Sending request to Deepseek API. Endpoint: {api_endpoint}")
        response = requests.post(
            api_endpoint, # Use the corrected variable
            headers=headers,
            json=data,
            timeout=90
        )

        logger.debug(f"Received response from Deepseek API. Status code: {response.status_code}")
        response.raise_for_status()

        result = response.json()
        logger.debug(f"Deepseek API Response (usage): {result.get('usage')}")
        if "choices" in result and len(result["choices"]) > 0:
              logger.debug(f"Deepseek API Response (finish_reason): {result['choices'][0].get('finish_reason')}")

        if "choices" in result and len(result["choices"]) > 0 and "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
            analysis_content = result["choices"][0]["message"]["content"].strip()
            # Basic validation: Check if it starts roughly as expected (Adjust if needed)
            # <<< MODIFIED: Changed expected start based on new prompt format
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
             if api_msg:
                 error_message += f" Message: {api_msg}"
             else:
                 error_message += f" Response: {response.text[:500]}"
         except requests.exceptions.JSONDecodeError:
             logger.error(f"API Response Text (non-JSON): {response.text[:500]}")
             error_message += f" Check API key, endpoint, model name, and request format. Response: {response.text[:200]}"
         return error_message

    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception occurred during Deepseek API call for {audio_filename}: {req_err}")
        # Specifically check for InvalidSchema which was the previous error
        if isinstance(req_err, requests.exceptions.InvalidSchema):
             logger.error(f"InvalidSchema error: The URL '{api_endpoint}' is likely malformed.") # Log the URL being used
        return f"Analysis failed: Network or connection error ({type(req_err).__name__})"
    except Exception as e:
        logger.exception(f"An unexpected error occurred during LLM analysis for {audio_filename}: {e}")
        return f"Analysis failed: Unexpected error ({type(e).__name__})"

def save_analysis_to_file(analysis_content, base_filename, analysis_folder):
    """Saves the analysis content to a text file."""
    try:
        # <<< MODIFIED: Create filename based on the input audio file's name
        analysis_filename = f"{os.path.splitext(base_filename)[0]}_analysis.txt"
        analysis_filepath = os.path.join(analysis_folder, analysis_filename)

        with open(analysis_filepath, 'w', encoding='utf-8') as f:
            f.write(analysis_content)
        logger.info(f"Analysis saved to: {analysis_filepath}")
        return True
    except Exception as e:
        logger.exception(f"Failed to save analysis file for {base_filename}: {e}")
        return False

# --- Main Processing Logic ---

# <<< MODIFIED: Renamed function and changed input parameter
def process_local_audio_file(audio_file_path, analysis_folder):
    """Transcribes, analyzes, and saves analysis for a single local audio file."""
    logger.info(f"Processing File: {audio_file_path}")
    analysis_result = "Analysis not performed"
    transcript = ""
    status = "Started"
    audio_filename = os.path.basename(audio_file_path) # Get the filename for logging/saving

    try:
        # <<< MODIFIED: Removed download step

        # 1. Transcribe (Was step 2)
        transcript = transcribe_audio(audio_file_path)
        if not transcript:
            logger.error(f"Transcription failed or resulted in empty text for {audio_filename}. Skipping analysis.")
            analysis_result = "Analysis skipped: Transcription failed or empty"
            status = "Transcription Failed"
        else:
            status = "Transcribed"

            # 2. Analyze (Was step 3)
            analysis_result = analyze_transcript_with_llm(transcript, audio_filename)
            if "Analysis failed" in analysis_result:
                status = "Analysis Failed"
                # Log the failure reason contained in analysis_result
                logger.error(f"Analysis failed for {audio_filename}: {analysis_result}")
            elif "Analysis skipped" in analysis_result:
                 status = "Analysis Skipped" # Should not happen if transcript exists
                 logger.warning(f"Analysis skipped for {audio_filename} despite transcript existing.")
            else:
                # 3. Save Analysis to File (Was step 4) (only on success)
                if save_analysis_to_file(analysis_result, audio_filename, analysis_folder):
                    status = "Analysis Success"
                else:
                    status = "Save Analysis Failed"
                    # Log the raw analysis to console as a fallback if saving failed
                    logger.error(f"Failed to save analysis file, logging result for {audio_filename} here:\n{analysis_result}")

    except Exception as e:
        logger.exception(f"An critical unexpected error occurred processing file {audio_filename}: {e}")
        analysis_result = f"Analysis failed: Critical error during processing ({type(e).__name__})"
        logger.error(analysis_result)
        status = "Critical Error"

    finally:
        # <<< MODIFIED: Removed audio file cleanup step
        logger.info(f"Finished processing attempt for File: {audio_filename}. Final Status: {status}")
        logger.info("-" * 70)
        return status

# <<< MODIFIED: Renamed function and changed logic to iterate through local files
def process_files_in_folder(input_folder=INPUT_AUDIO_FOLDER, analysis_folder=ANALYSIS_FOLDER):
    """Lists audio files in a folder, then processes each file individually and reports summary."""
    audio_files = list_audio_files(input_folder)
    if not audio_files:
        logger.warning("No MP3/WAV files found in the input folder or folder couldn't be read. Exiting.")
        return

    total_files = len(audio_files)
    logger.info(f"Starting processing for {total_files} files from {input_folder}...")
    logger.info(f"Analysis results will be saved in: {os.path.abspath(analysis_folder)}")

    status_counts = {
        "Analysis Success": 0,
        # "Download Failed": 0, # <<< MODIFIED: Removed status
        "Transcription Failed": 0,
        "Analysis Failed": 0,
        "Analysis Skipped": 0,
        "Save Analysis Failed": 0,
        "Critical Error": 0,
        "Started": 0, # Should ideally not be a final state
        "Unknown": 0
    }

    for i, filename in enumerate(audio_files, 1):
        logger.info(f"--- Processing File {i}/{total_files} ---")
        file_path = os.path.join(input_folder, filename)
        final_status = "Unknown"
        try:
            # Pass the full file path and analysis folder path to the processing function
            final_status = process_local_audio_file(file_path, analysis_folder)

        except Exception as loop_err:
            logger.error(f"A critical error occurred in the main loop for file {filename}, attempting to continue: {loop_err}")
            final_status = "Critical Error"

        # Use .get() with a default for safety in case an unexpected status string is returned
        status_counts[final_status] = status_counts.get(final_status, 0) + 1

    # Log Summary Report
    logger.info("=" * 70)
    logger.info("Processing Summary:")
    logger.info(f"Total Files Attempted: {total_files}")
    for status, count in status_counts.items():
         if count > 0:
             logger.info(f"- {status}: {count}")
    logger.info(f"Analysis results saved in: {os.path.abspath(analysis_folder)}")
    logger.info("=" * 70)

# --- Script Execution ---

if __name__ == "__main__":
    logger.info("Script started. Log file: %s", log_file)
    if not dateutil_available:
         logger.warning("python-dateutil library not found (pip install python-dateutil). Age calculation will be approximate.")

    # Ensure analysis folder exists before starting processing
    try:
        os.makedirs(ANALYSIS_FOLDER, exist_ok=True)
    except OSError as e:
        logger.error(f"Could not create analysis directory '{ANALYSIS_FOLDER}': {e}. Exiting.")
        exit(1)

    # <<< MODIFIED: Check if input folder exists
    if not os.path.isdir(INPUT_AUDIO_FOLDER):
         logger.error(f"The specified input audio folder does not exist or is not a directory: {INPUT_AUDIO_FOLDER}")
         logger.error("Please check the INPUT_AUDIO_FOLDER path at the beginning of the script.")
         exit(1)

    # <<< MODIFIED: Call the updated processing function
    process_files_in_folder() # Uses defaults defined at the top

    logger.info("Script finished.")