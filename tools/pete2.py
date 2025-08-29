import requests
import openai
import time
import json
import os
from pydub import AudioSegment  # Importing for converting .wav to .mp3

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

def read_urls_from_file(file_name='urls.txt'):
    """Reads URLs from a file and returns a list of URLs."""
    with open(file_name, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls if url.strip()]

def download_audio(url, file_name):
    """Downloads an audio file (e.g., .wav) from a given URL."""
    response = requests.get(url)
    with open(file_name, 'wb') as file:
        file.write(response.content)

def convert_wav_to_mp3(wav_file, mp3_file):
    """Converts a .wav file to .mp3 using pydub."""
    audio = AudioSegment.from_wav(wav_file)
    audio.export(mp3_file, format="mp3")

def upload_audio_to_assemblyai(file_path):
    """Uploads an audio file to AssemblyAI and returns the upload URL."""
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    try:
        with open(file_path, 'rb') as f:
            response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files={'file': f})
            response.raise_for_status()  # Raise error for bad status codes
            response_data = response.json()  # Safely decode JSON
            return response_data.get('upload_url', None)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
    except ValueError:
        print("Error decoding JSON response.")
    return None  # Return None if there's an error

def transcribe_audio(assemblyai_url):
    """Submits an audio file for transcription on AssemblyAI and waits for the transcription to complete."""
    headers = {'authorization': ASSEMBLYAI_API_KEY, 'content-type': 'application/json'}
    json_data = {'audio_url': assemblyai_url}
    try:
        response = requests.post('https://api.assemblyai.com/v2/transcript', json=json_data, headers=headers)
        response.raise_for_status()
        transcript_id = response.json().get('id')
        
        if transcript_id:
            while True:
                check_response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
                check_response.raise_for_status()
                check_data = check_response.json()
                
                if check_data['status'] == 'completed':
                    return check_data['text']
                elif check_data['status'] == 'failed':
                    return "Transcription failed"
                time.sleep(2)
        else:
            print("No transcription ID received.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
    except ValueError:
        print("Error decoding JSON response.")
    return None

def analyze_transcript_with_chatgpt(transcript):
    """
    Analyzes the call transcript using ChatGPT-4o to determine various aspects of the call.
    """
    prompt = f"""
    {transcript}

### Objectives:

You are an expert in phone call analysis. Based on the provided call transcript between our insurance agent AI and the customer, evaluate the following aspects:

**Customer Contact Details:**  
Customer Full Name:  
Customer Phone Number:

1. **Customer's Engagement**:  
   - Did the customer answer the phone call?

2. **Customer's Response to Consent Preparation**:  
   - What was the customer's response to the question: *"However, if there’s been a misunderstanding, I’d be glad to send you the necessary consent forms and documents to prepare for 2025 and tackle any potential fraud issues. Does that sound good to you?"*

3. **Customer's Response to Enrollment Consent**:  
   - What was the customer's answer to: *"To send you the link, we need your consent. Do you give Aaronson Insurance Group permission to search and enroll you in the best possible Marketplace health plan and contact you moving forward?"*

4. **Response to Additional Insurance Options**:  
   - How did the customer respond to: *"Great! There are also new dental, vision, and life insurance add-ons available. Is that something you’d be interested in?"*

5. **Phone Callback**:  
   - Did the customer request a call back?

6. **Appointment Confirmation**:  
   - Was an appointment scheduled? If so, please provide the **date and time**.

7. **Call Summary**:  
   - Provide a brief, concise summary of the key points and outcomes of the call.

---

**Response Example:**

John Smith  
8655551212

1. Yes  
2. Yes  
3. No  
4. Yes  
5. Yes  
6. No

7. The customer answered the call, consented to preparation for 2025 fraud protection, but declined the enrollment. They expressed interest in additional insurance options but did not schedule an appointment.
[    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a highly intelligent AI trained to analyze call transcripts for insurance purposes."},
            {"role": "user", "content": prompt}
        ]
    )
    
    if response and 'choices' in response and response['choices']:
        analysis_result = response['choices'][0]['message']['content']
        return analysis_result.strip()
    else:
        return "Analysis failed due to an error."

def process_call(url):
    """Orchestrates the process of handling a call: downloading, converting, uploading for transcription, and analyzing."""
    temp_wav_file = 'temp_audio.wav'
    temp_mp3_file = 'temp_audio.mp3'
    try:
        # Step 1: Download the .wav file
        download_audio(url, temp_wav_file)
        
        # Step 2: Convert .wav to .mp3
        convert_wav_to_mp3(temp_wav_file, temp_mp3_file)
        
        # Step 3: Upload the .mp3 file to AssemblyAI for transcription
        assemblyai_url = upload_audio_to_assemblyai(temp_mp3_file)
        
        # Step 4: Transcribe the audio
        transcript = transcribe_audio(assemblyai_url)
        
        # Step 5: Analyze the transcript using ChatGPT
        analysis_result = analyze_transcript_with_chatgpt(transcript)
    finally:
        # Clean up by removing the temporary audio files
        try:
            if os.path.exists(temp_wav_file):
                os.remove(temp_wav_file)
            if os.path.exists(temp_mp3_file):
                os.remove(temp_mp3_file)
        except PermissionError:
            print(f"Failed to delete {temp_mp3_file}. It might still be in use.")

    return analysis_result

def process_all_calls():
    """Processes all calls from the URLs provided in the 'urls.txt' file."""
    urls = read_urls_from_file()
    for url in urls:
        print(f"Processing: {url}")
        result = process_call(url)
        print("Analysis Result:\n", result)
        print("---------------------------------------------------")

if __name__ == "__main__":
    process_all_calls()
