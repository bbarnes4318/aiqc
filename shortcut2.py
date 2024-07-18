import requests
import openai
import time
import json
import os

ASSEMBLYAI_API_KEY = 'c34fcd7703954d55b39dba9ec1a7b04c'
OPENAI_API_KEY = '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'
openai.api_key = OPENAI_API_KEY

def read_urls_from_file(file_name='urls.txt'):
    """
    Reads URLs from a file and returns a list of URLs.
    """
    with open(file_name, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls if url.strip()]

def download_mp3(url, file_name):
    """
    Downloads an MP3 file from a given URL.
    """
    response = requests.get(url)
    with open(file_name, 'wb') as file:
        file.write(response.content)

def upload_audio_to_assemblyai(file_path):
    """
    Uploads an audio file to AssemblyAI and returns the upload URL.
    """
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    response = requests.post('https://api.assemblyai.com/v2/upload',
                             headers=headers,
                             files={'file': open(file_path, 'rb')})
    return response.json()['upload_url']

def transcribe_audio(assemblyai_url):
    """
    Submits an audio file for transcription on AssemblyAI and waits for the transcription to complete.
    """
    headers = {'authorization': ASSEMBLYAI_API_KEY, 'content-type': 'application/json'}
    json_data = {'audio_url': assemblyai_url}
    response = requests.post('https://api.assemblyai.com/v2/transcript', json=json_data, headers=headers)
    transcript_id = response.json()['id']

    # Polling for the transcript completion
    while True:
        check_response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
        if check_response.json()['status'] == 'completed':
            return check_response.json()['text']
        elif check_response.json()['status'] == 'failed':
            return "Transcription failed"
        
def analyze_transcript_with_chatgpt(transcript):
    prompt = f"""
    Analyze the following call transcript:
    {transcript}
    
    Based on the transcript, determine:
    1. A brief call summary including key details and outcomes.
    2. If the call is billable. A call is not billable if any of the following is true:
       - The prospect lives in a nursing home.
       - The prospect does not have a bank account, debit card, or credit card.
       - The prospect needs a power of attorney present when making financial decisions.
       - The prospect is 81 years old or older.
       - The prospect does not know they are on the call to speak with an agent regarding final expense or life insurance.
    3. If a quote for final expense or life insurance was given.
    4. If a sale was made, indicated by the prospect providing their bank account and routing numbers or their credit card number. Include the insurance carrier and monthly premium if available.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",  # Adjust the model as necessary
            messages=[
                {"role": "system", "content": "You are a highly intelligent AI trained to analyze call transcripts for insurance purposes."},
                {"role": "user", "content": prompt}
            ]
        )
        # Extracting the analysis result from the response
        if response and response['choices']:
            analysis_result = response['choices'][0]['message']['content']
            return analysis_result.strip()
        else:
            return "No analysis result."
    except Exception as e:
        print(f"Error during ChatGPT analysis: {e}")
        return None

def process_call(url):
    """
    Orchestrates the process of handling a call: downloading, uploading for transcription, transcribing, and analyzing.
    """
    temp_file_name = 'temp_audio.mp3'
    try:
        download_mp3(url, temp_file_name)
        assemblyai_url = upload_audio_to_assemblyai(temp_file_name)
        transcript = transcribe_audio(assemblyai_url)
        analysis_result = analyze_transcript_with_chatgpt(transcript)
    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
    
    return analysis_result

def process_all_calls():
    """
    Processes all calls from the URLs provided in the 'urls.txt' file.
    """
    urls = read_urls_from_file()
    if not urls:
        print("No URLs found in the file.")
        return

    for url in urls:
        if not url:
            print("Encountered an empty or invalid URL, skipping...")
            continue
        print(f"Processing: {url}")
        result = process_call(url)
        print("Analysis Result:", result)
        print("---------------------------------------------------")

process_all_calls()