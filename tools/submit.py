import requests
import openai
import time
import json
import os

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
    
    # Check if the initial request was successful
    if response.status_code != 200:
        print(f"Failed to submit the audio file: {response.text}")
        return None
    
    response_data = response.json()
    if 'id' not in response_data:
        print(f"Error: 'id' key not found in response data. Full response: {response_data}")
        return None

    transcript_id = response_data['id']
    while True:
        check_response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
        check_response_data = check_response.json()

        if check_response.status_code != 200:
            print(f"Error checking transcript status: {check_response.text}")
            return None

        if check_response_data['status'] == 'completed':
            return check_response_data['text']
        elif check_response_data['status'] == 'failed':
            print(f"Transcription failed with message: {check_response_data.get('error', 'No error message available')}")
            return "Transcription failed"
        
        # Delay the next status check to avoid too frequent requests
        time.sleep(5)  # sleep for 5 seconds before next check

def analyze_transcript_with_chatgpt(transcript):
    """
    Analyzes the call transcript using ChatGPT-4 to determine various aspects of the call.
    """
    prompt = f"""
    Analyze the following call transcript:
    {transcript}

Purpose: Evaluate live transfer calls to determine if a final expense insurance application was submitted and assess the billability of the call.

Process Overview:

1.Application Submission Check-Analyze the call to identify if an application was submitted. If any of the following occur during the call then it is an indicator that an application was submitted:
-Prospect provides their bank account routing number and account number.
-Prospect provides their debit or credit card number.
-A third party is brought onto the call for verification purposes.
-The agent explicitly states that an application has been submitted.

2. Whether the call is billable. A call is billable unless ANY of the following are true:
       - The prospect lives in a nursing home or an assisted living facility.
       - The prospect does not have a bank account, debit card, or credit card.
       - The prospect needs a power of attorney present when making financial decisions.
       - The prospect is unaware they are on the call to speak with an agent regarding final expense or life insurance.
       - The prospect is only on the call to waste the agent’s time or it's a prank call
       - The prospect is 81 years old or more
       - The prospect has been diagnosed with Alzheimer’s or dementia

Required AI Outputs:

Application Status: Was an application submitted? (Yes/No)
	-If Yes, capture the following details:
		-Monthly Premium
		-Carrier
		-Coverage Amount
		-First Payment Date
		-Policy Type (Level, Graded, Modified, Guaranteed Issue)

Call Billability: Is the call billable? (Yes/No)
	-If No, specify the reason based on the conditions listed above.

Licensed Agent:
-The name of the licensed agent

Prospect Information:
-Full Name (or first name if full name is unavailable)
-Phone Number

Quote Information (if no application submitted):
-Was a quote given? (Yes/No)
	-If Yes, provide details:
		-Name of Carrier Quoted
		-Coverage Quoted
		-Premium Quoted
		-Reason for not purchasing (Price, needs consultation, lacks banking info, privacy concerns, no perceived need, other)

Follow-Up Actions:
-Was a follow-up date set? (Yes/No)
	-If Yes, specify the follow-up date.
	-Should the agent follow up with the prospect? (Yes/No)

Instructions for AI:

-Analyze both verbal and non-verbal cues from the recorded call data.

-Utilize natural language processing to detect explicit and implied statements related to the criteria listed.

-Organize the extracted information into the structured format outlined above for clear communication to stakeholders.

-Ensure high accuracy to aid agents in making informed decisions about further actions with each prospect.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",
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
    """Orchestrates the process of handling a call: downloading, uploading for transcription, transcribing, and analyzing."""
    temp_file_name = 'temp_audio.mp3'
    try:
        download_mp3(url, temp_file_name)
        assemblyai_url = upload_audio_to_assemblyai(temp_file_name)
        transcript = transcribe_audio(assemblyai_url)
        analysis_result = analyze_transcript_with_chatgpt(transcript)
    finally:
        # Clean up by removing the temporary audio file
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
    
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
