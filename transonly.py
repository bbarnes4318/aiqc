import requests
import os

# AssemblyAI API key
api_key = 'your_assemblyai_api_key'

def transcribe(file_path):
    def upload_file(file_path):
        headers = {'authorization': api_key}
        with open(file_path, 'rb') as f:
            response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files={'file': f})
        return response.json()['upload_url']

    def get_transcription(upload_url):
        json = {"audio_url": upload_url}
        headers = {"authorization": api_key, "content-type": "application/json"}
        response = requests.post('https://api.assemblyai.com/v2/transcript', json=json, headers=headers)
        return response.json()['id']

    def check_status(transcript_id):
        endpoint = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'
        headers = {"authorization": api_key}
        while True:
            response = requests.get(endpoint, headers=headers)
            status = response.json()['status']
            if status == 'completed':
                return response.json()['text']
            elif status == 'failed':
                return 'Transcription failed'

    upload_url = upload_file(file_path)
    transcript_id = get_transcription(upload_url)
    return check_status(transcript_id)

# Directory containing MP3 files
directory = 'path_to_your_directory_with_mp3s'

# Iterate over each file in the directory and transcribe
for file_name in os.listdir(directory):
    if file_name.endswith('.mp3'):
        file_path = os.path.join(directory, file_name)
        print(f"Transcribing file {file_name}...")
        transcription = transcribe(file_path)
        print(f"Transcription for file {file_name}:")
        print(transcription)
