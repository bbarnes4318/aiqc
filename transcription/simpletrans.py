import requests
import time
import json
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')

def get_audio_files(directory):
    """Returns a list of audio file paths from the specified directory."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.mp3')]

def upload_audio_to_assemblyai(file_path):
    """Uploads an audio file to AssemblyAI and returns the upload URL."""
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    response = requests.post('https://api.assemblyai.com/v2/upload',
                             headers=headers,
                             files={'file': open(file_path, 'rb')})
    return response.json()['upload_url']

def transcribe_audio(assemblyai_url):
    """Submits an audio file for transcription on AssemblyAI and waits for the transcription to complete."""
    headers = {'authorization': ASSEMBLYAI_API_KEY, 'content-type': 'application/json'}
    json_data = {'audio_url': assemblyai_url}
    response = requests.post('https://api.assemblyai.com/v2/transcript', json=json_data, headers=headers)
    transcript_id = response.json()['id']

    while True:
        check_response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
        if check_response.json()['status'] == 'completed':
            return check_response.json()['text']
        elif check_response.json()['status'] == 'failed':
            return "Transcription failed"

def process_audio_file(file_path):
    """Orchestrates the process of handling an audio file: uploading for transcription, and displaying the transcript."""
    try:
        assemblyai_url = upload_audio_to_assemblyai(file_path)
        transcript = transcribe_audio(assemblyai_url)
    except Exception as e:
        return f"Error processing file {file_path}: {str(e)}"
    
    return transcript

def process_all_audio_files(directory):
    """Processes all audio files in the specified directory."""
    files = get_audio_files(directory)
    for file_path in files:
        print(f"Processing: {file_path}")
        transcript = process_audio_file(file_path)
        print("Transcript:\n", transcript)
        print("---------------------------------------------------")

if __name__ == "__main__":
    audio_directory = r'C:\Users\Jimbo\Desktop\FE Python Transcription App\audios'
    process_all_audio_files(audio_directory)