import requests
import openai
import time
import json
import os
from pydub import AudioSegment  # For converting WAV to MP3

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# API Keys
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Step 1: Read URLs from file
def read_urls_from_file(file_name='urls.txt'):
    with open(file_name, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls if url.strip()]

# Step 2: Download audio
def download_audio(url, file_name):
    response = requests.get(url)
    with open(file_name, 'wb') as file:
        file.write(response.content)

# Step 3: Convert WAV to MP3
def convert_wav_to_mp3(wav_file, mp3_file):
    audio = AudioSegment.from_wav(wav_file)
    audio.export(mp3_file, format="mp3")

def upload_audio_to_assemblyai(file_path):
    # AssemblyAI upload endpoint and headers
    upload_endpoint = "https://api.assemblyai.com/v2/upload"
    headers = {
        'authorization': ASSEMBLYAI_API_KEY
    }

    try:
        with open(file_path, 'rb') as audio_file:
            response = requests.post(upload_endpoint, headers=headers, files={'file': audio_file})
        
        if response.status_code != 200:
            print(f"Error: Failed to upload file, status code: {response.status_code}")
            print(f"Response: {response.text}")  # Log the error response for better debugging
            return None

        return response.json().get('upload_url')
    except Exception as e:
        print(f"Exception during file upload: {e}")
        return None

# Step 5: Transcribe audio using AssemblyAI
def transcribe_audio(upload_url):
    transcribe_endpoint = "https://api.assemblyai.com/v2/transcript"
    headers = {
        'authorization': ASSEMBLYAI_API_KEY,
        'content-type': 'application/json'
    }
    data = json.dumps({'audio_url': upload_url})

    response = requests.post(transcribe_endpoint, headers=headers, data=data)
    if response.status_code != 200:
        print(f"Error: Transcription failed, status code: {response.status_code}")
        return None

    transcript_id = response.json()['id']
    return transcript_id

# Step 6: Fetch transcription result
def get_transcription_result(transcript_id):
    transcribe_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {'authorization': ASSEMBLYAI_API_KEY}

    while True:
        response = requests.get(transcribe_endpoint, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'completed':
                return data['text']
            elif data['status'] == 'failed':
                print("Transcription failed.")
                return None
        time.sleep(5)

# Step 7: Analyze transcription using OpenAI GPT
def analyze_transcription(transcription_text):
    # Prompt setup with your specific request logic
    prompt = f"""
    ### Objectives:

    Based on the call transcript, you are tasked with determining the following:

    ## You are an expert in phone call analysis. Use the transcription provided to evaluate the following aspects of a phone call between our insurance agent AI and the customer:

    **Customer Contact Details:**
    Customer Full Name:
    Customer Phone Number: 

    1. **Customer's Engagement**: Did the customer answer the phone call?

    2. **Customer's Response to Consent Preparation**: 
       - What was the customer's response to the question: *"However, if there’s been a misunderstanding, I’d be glad to send you the necessary consent forms and documents to prepare for 2025 and tackle any potential fraud issues. Does that sound good to you?"*

    3. **Customer's Response to Enrollment Consent**: 
       - What was the customer's answer to: *"To send you the link, we need your consent. Do you give Aaronson Insurance Group permission to search and enroll you in the best possible Marketplace health plan and contact you moving forward?"

    4. **Response to Additional Insurance Options**: 
       - How did the customer respond to: *"Great! There are also new dental, vision, and life insurance add-ons available. Is that something you’d be interested in?"*

    5. **Phone Callback**:
       - Did the customer request a call back?

    6. **Appointment Confirmation**: 
       - Was an appointment scheduled? If so, please provide the **date and time**.

    7. **Call Summary**: 
       - Provide a brief, concise summary of the key points and outcomes of the call.


    **Response Example:** 

    John Smith
    8655551212

    1. Yes
    2. Yes
    3. No
    4. Yes
    5. Yes
    6. No

    7. Summarize the phone call here
    """

    # Call OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt + f"\n\nTranscript: {transcription_text}",
        max_tokens=500,
        temperature=0.5
    )

    return response.choices[0].text.strip()

# Step 8: Full process for all URLs
def process_all_calls():
    urls = read_urls_from_file()
    for url in urls:
        print(f"Processing: {url}")

        # Download the audio file
        wav_file = "audio.wav"
        download_audio(url, wav_file)

        # Convert to MP3
        mp3_file = "audio.mp3"
        convert_wav_to_mp3(wav_file, mp3_file)

        # Upload to AssemblyAI
        upload_url = upload_audio_to_assemblyai(mp3_file)
        if not upload_url:
            continue

        # Transcribe the audio
        transcript_id = transcribe_audio(upload_url)
        if not transcript_id:
            continue

        # Fetch the transcription
        transcription_result = get_transcription_result(transcript_id)
        if transcription_result:
            # Analyze the transcription using OpenAI GPT
            analysis_result = analyze_transcription(transcription_result)
            print(f"Analysis Result:\n{analysis_result}")
        else:
            print("Failed to fetch transcription.")

# Run the process for all calls
process_all_calls()
