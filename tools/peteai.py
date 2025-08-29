import requests
import os
import subprocess
import openai
import time
import json

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# API Keys
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY  # Set OpenAI API key

# Text file path
output_dir = "C:\\Users\\Jimbo\\Desktop\\vapi-pull"
results_file_path = os.path.join(output_dir, "results.txt")

# Ensure the directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Step 1: Read URLs from file
def read_urls_from_file(file_name='urls.txt'):
    with open(file_name, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls if url.strip()]

# Step 2: Download audio
def download_audio(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {file_name}, size: {os.path.getsize(file_name)} bytes")
    else:
        print(f"Failed to download {file_name}. Status code: {response.status_code}")

# Step 3: Convert audio to MP3 using ffmpeg (regardless of format)
def convert_to_mp3(audio_file, mp3_file):
    try:
        subprocess.run(['ffmpeg', '-y', '-i', audio_file, mp3_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Converted {audio_file} to {mp3_file} successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")

# Step 4: Upload the MP3 file to AssemblyAI
def upload_audio_to_assemblyai(file_path):
    upload_endpoint = "https://api.assemblyai.com/v2/upload"
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    try:
        with open(file_path, 'rb') as audio_file:
            response = requests.post(upload_endpoint, headers=headers, files={'file': audio_file})
        if response.status_code != 200:
            print(f"Error: Failed to upload file, status code: {response.status_code}")
            return None
        return response.json().get('upload_url')
    except Exception as e:
        print(f"Exception during file upload: {e}")
        return None

# Step 5: Transcribe audio using AssemblyAI
def transcribe_audio(upload_url):
    transcribe_endpoint = "https://api.assemblyai.com/v2/transcript"
    headers = {'authorization': ASSEMBLYAI_API_KEY, 'content-type': 'application/json'}
    data = json.dumps({'audio_url': upload_url})

    response = requests.post(transcribe_endpoint, headers=headers, data=data)
    if response.status_code != 200:
        print(f"Error: Transcription failed, status code: {response.status_code}")
        return None
    return response.json()['id']

# Step 6: Fetch transcription result from AssemblyAI
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
        else:
            print(f"Error fetching transcription status: {response.status_code}")
            return None
        time.sleep(5)

# Step 7: Analyze transcription using GPT-4 with custom prompt
def analyze_transcription(transcription_text):
    prompt = f"""
1. Did a human being answer the phone?
   Provide a Yes or No.

If Yes:
2. Is maintaining health insurance coverage a priority for the coming year?
   Provide a Yes or No.

3. Did the customer give permission for Aaronson Insurance Group to act as their agent of record?
   Provide a Yes or No.

4. Was there an interest expressed in new add-ons (dental, vision, life insurance)?
   Provide a Yes or No.

5. Was a callback or appointment scheduled with the customer?
   Provide Yes or No.

6. Summary of the call:
   Briefly summarize the call.

Transcript: {transcription_text}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI that analyzes text transcriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error during OpenAI analysis: {e}")
        return None

# Step 8: Write analysis results to the text file
def write_results_to_text(recording_url, analysis_result):
    print("Writing results to text file...")
    print(f"Analysis result for {recording_url}: {analysis_result}")  # Debugging

    try:
        with open(results_file_path, mode="a", encoding="utf-8") as file:
            file.write(f"Recording URL: {recording_url}\n")
            # Split the analysis_result into lines and write each
            for line in analysis_result.strip().split('\n'):
                file.write(f"{line}\n")
            file.write("-" * 50 + "\n")  # Separator for readability
    except Exception as e:
        print(f"Error writing to text file: {e}")

# Step 9: Full process for all URLs
def process_all_calls():
    urls = read_urls_from_file()
    for url in urls:
        print(f"Processing: {url}")

        # Download the audio file
        audio_file = "audio.wav"
        download_audio(url, audio_file)

        # Convert to MP3
        mp3_file = "audio.mp3"
        convert_to_mp3(audio_file, mp3_file)

        # Upload to AssemblyAI
        upload_url = upload_audio_to_assemblyai(mp3_file)
        if not upload_url:
            print("Skipping to next URL due to upload failure.")
            continue

        # Transcribe the audio
        transcript_id = transcribe_audio(upload_url)
        if not transcript_id:
            print("Skipping to next URL due to transcription initiation failure.")
            continue

        # Fetch the transcription
        transcription_result = get_transcription_result(transcript_id)
        if transcription_result:
            # Analyze the transcription
            analysis_result = analyze_transcription(transcription_result)
            if analysis_result:
                print(f"Analysis Result:\n{analysis_result}")
                # Write the result to the text file
                write_results_to_text(url, analysis_result)
            else:
                print("Failed to analyze transcription.")
        else:
            print("Failed to fetch transcription.")

        # Cleanup: Remove downloaded and converted files to save space
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
            if os.path.exists(mp3_file):
                os.remove(mp3_file)
        except Exception as e:
            print(f"Error during cleanup: {e}")

    print(f"Results successfully written to '{results_file_path}'.")

# Run the process for all calls
if __name__ == "__main__":
    process_all_calls()
