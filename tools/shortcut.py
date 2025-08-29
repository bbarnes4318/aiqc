import requests
import openai
import time
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Function to read URLs from a file
def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# Function to download MP3 from URL
def download_mp3(url, file_name):
    response = requests.get(url)
    with open(file_name, 'wb') as file:
        file.write(response.content)
    return file_name

def transcribe_audio_with_assemblyai(audio_file_path):
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files={'file': open(audio_file_path, 'rb')})
    audio_id = response.json()['upload_url']

    transcription_request = {"audio_url": audio_id}
    response = requests.post('https://api.assemblyai.com/v2/transcript', json=transcription_request, headers=headers)
    transcript_id = response.json()['id']

    while True:
        transcript_response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
        if transcript_response.json()['status'] == 'completed':
            return transcript_response.json()['text']
        elif transcript_response.json()['status'] == 'failed':
            return "Transcription failed."
        time.sleep(5)

def analyze_transcript_with_gpt3_turbo(transcript):
    prompt = f"""
    Given the following call transcript, please provide:

    1. A brief summary of the call, including key details and outcomes.
    2. Determine if the call is billable based on specific criteria.
    3. Indicate if a quote for final expense or life insurance was given.
    4. Determine if a sale was made, noting the insurance carrier and the monthly premium if applicable.

    Transcript:
    "{transcript}"
    """
    
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  
            prompt=prompt,
            max_tokens=1024,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0,
            presence_penalty=0,
            user="your_user_id_here"  # if required for your specific model or API setup
        )

        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error analyzing transcript: {str(e)}")
        return "Analysis error."

# Ensure the rest of your script remains the same.

# Main workflow
def process_audio_files_from_urls(file_path):
    urls = read_urls_from_file(file_path)
    for index, url in enumerate(urls):
        file_name = f"audio_{index}.mp3"
        print(f"Downloading {url} to {file_name}...")
        download_mp3(url, file_name)
        
        print(f"Transcribing {file_name}...")
        transcript = transcribe_audio_with_assemblyai(file_name)
        if transcript != "Transcription failed.":
            analysis = analyze_transcript_with_gpt3_turbo(transcript)
            print(f"Analysis Results for {file_name}:\n{analysis}")
        else:
            print(f"Failed to transcribe {file_name}.")
        
        # Optional: Clean up by deleting the downloaded MP3 file after processing
        os.remove(file_name)

if __name__ == "__main__":
    file_path = 'urls.txt'  # File containing URLs to audio files
    process_audio_files_from_urls(file_path)


