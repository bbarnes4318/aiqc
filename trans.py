import requests
import openai
import json
import os
import time

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

def download_mp3(url, file_name):
    """Downloads an MP3 file from a given URL."""
    response = requests.get(url)
    with open(file_name, 'wb') as file:
        file.write(response.content)

def transcribe_audio(file_path):
    """Transcribes audio using AssemblyAI."""
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    
    try:
        # Upload the audio file
        upload_response = requests.post(
            'https://api.assemblyai.com/v2/upload',
            headers=headers,
            data=open(file_path, 'rb')
        )
        upload_response.raise_for_status()  # Check for HTTP errors
        upload_url = upload_response.json().get('upload_url')
        
        if not upload_url:
            print("Error: Upload URL not found in the response.")
            return None
        
        # Request transcription
        transcript_request = {'audio_url': upload_url}
        transcript_response = requests.post(
            'https://api.assemblyai.com/v2/transcript',
            json=transcript_request,
            headers=headers
        )
        transcript_response.raise_for_status()  # Check for HTTP errors
        
        transcript_id = transcript_response.json().get('id')
        if not transcript_id:
            print("Error: Transcript ID not found in the response.")
            return None
        
        # Polling for the transcription result
        while True:
            status_response = requests.get(
                f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
                headers=headers
            )
            status_response.raise_for_status()  # Check for HTTP errors
            status_json = status_response.json()
            
            # Debugging: Print the entire response to see the structure
            print("Debugging response:", status_json)
            
            status = status_json.get('status')
            if status == 'completed':
                return status_json.get('text')
            elif status == 'failed':
                print("Transcription failed.")
                return None
            
            time.sleep(5)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    except KeyError as e:
        print(f"Unexpected response structure, missing key: {e}")
        print(status_response.json())
        return None

def format_transcription(transcription):
    """Formats the transcription for client presentation."""
    formatted_text = f"""
    --------------------------------------------
    TRANSCRIPTION REPORT
    --------------------------------------------
    
    Date: {time.strftime("%Y-%m-%d")}
    Time: {time.strftime("%H:%M:%S")}
    
    --------------------------------------------
    TRANSCRIPTION:
    --------------------------------------------
    
    {transcription}
    
    --------------------------------------------
    END OF TRANSCRIPTION
    --------------------------------------------
    """
    return formatted_text

def main():
    urls = read_urls_from_file('urls.txt')
    for idx, url in enumerate(urls):
        mp3_file_name = f'audio_{idx}.mp3'
        download_mp3(url, mp3_file_name)
        transcription = transcribe_audio(mp3_file_name)
        if transcription:
            formatted_transcription = format_transcription(transcription)
            with open(f'transcription_{idx}.txt', 'w') as file:
                file.write(formatted_transcription)
            print(f"Transcription saved as transcription_{idx}.txt")
        else:
            print(f"Failed to transcribe {mp3_file_name}")

if __name__ == '__main__':
    main()
