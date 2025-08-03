import requests
import openai
import time
import json
import os
import csv

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

CSV_FILE_PATH = r"C:\Users\Jimbo\crm-dashboard\results.csv"

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
    transcript_id = response.json()['id']

    while True:
        check_response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
        if check_response.json()['status'] == 'completed':
            return check_response.json()['text']
        elif check_response.json()['status'] == 'failed':
            return "Transcription failed"

def analyze_transcript_with_chatgpt(transcript):
    """
    Analyzes the call transcript using ChatGPT-4 to determine various aspects of the call.
    """
    prompt = f"""
    Analyze the following call transcript:
    {transcript}

# AI Task: Determining Call Outcomes from Transcripts

## Task Description:
You are tasked with analyzing call transcripts between our AI Voice Agent and ACA Health Insurance customers. Your goal is to determine specific outcomes of each call by identifying key information, and output the results as Boolean values (TRUE or FALSE) for each of the seven predefined categories, including date and time where applicable. **Note**: There cannot be both an appointment and a callback. An appointment must include a specific date and time, while a callback does not.

## Instructions:
1. **Read the provided call transcript carefully.**
2. **For each of the seven categories, determine whether the condition is met (TRUE or FALSE).**
3. **If an appointment was made, extract the specific date and time.**
4. **Ensure that both 'appointment' and 'callback' cannot be TRUE at the same time.**
5. **Provide a brief justification for each determination, citing relevant parts of the transcript.**
6. **Present your findings in the specified output format.**

## Categories and Definitions:
### 1. **contacted**: Did the customer answer the phone call and speak to our AI?
- **TRUE** if the customer engaged in any conversation.
- **FALSE** if the call was unanswered or there was no interaction.

### 2. **renewal**: Did the customer agree to receive renewal documents by email?
- **TRUE** if the customer consented to receive documents via email.
- **FALSE** otherwise.

### 3. **consent**: Did the customer give consent for the agency or agent to continue acting as their Agent of Record?
- **TRUE** if the customer explicitly agreed.
- **FALSE** otherwise.

### 4. **appointment**: Did the customer agree to a specific time to meet with an agent?
- **TRUE** if a specific appointment date and time were scheduled.
- **FALSE** if no specific date and time were provided.
- **Note**: If TRUE, extract the exact **date** and **time** of the appointment.

### 5. **callback**: Did the customer request a callback (not a specific time like an appointment)?
- **TRUE** if the customer asked to be called back without specifying a time.
- **FALSE** otherwise.
- **Note**: **Both 'appointment' and 'callback' cannot be TRUE** at the same time. An appointment includes a specific date and time, while a callback does not.

### 6. **addons**: Did the customer express interest in life insurance or dental insurance?
- **TRUE** if the customer showed interest in additional insurance products.
- **FALSE** otherwise.

### 7. **remove**: Did the customer ask us to stop calling?
- **TRUE** if the customer requested no further contact.
- **FALSE** otherwise.

## Output Format:
Please present your findings as follows:

```vbnet
contacted: TRUE/FALSE - [Brief Justification]
renewal: TRUE/FALSE - [Brief Justification]
consent: TRUE/FALSE - [Brief Justification]
appointment: TRUE/FALSE - [Date and Time, if applicable; otherwise, provide justification]
callback: TRUE/FALSE - [Brief Justification]
addons: TRUE/FALSE - [Brief Justification]
remove: TRUE/FALSE - [Brief Justification]

Example:
contacted: TRUE - The customer answered and spoke with the AI.
renewal: FALSE - No agreement to receive documents by email was made.
consent: TRUE - Customer consented to continue as Agent of Record.
appointment: TRUE - Appointment set for 2024-09-15 at 10:30 AM.
callback: FALSE - An appointment with a specific date and time was scheduled.
addons: FALSE - No interest in additional insurance expressed.
remove: FALSE - Customer did not ask to stop calling.

Additional Guidelines:
Accuracy is crucial: Base your determinations solely on the transcript content.

Be objective: Do not make assumptions beyond the provided information.

Appointment and Callback Exclusivity: If the customer agreed to a specific appointment (with date and time), the callback should be marked as FALSE. Conversely, if the customer requested a callback without a specific time, the appointment should be marked FALSE.

Confidentiality: Ensure all customer data is handled per privacy regulations.

Please proceed by analyzing the provided transcript following the guidelines above.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",
        messages=[{"role": "system", "content": "You are a highly intelligent AI trained to analyze call transcripts for insurance purposes."},
                  {"role": "user", "content": prompt}]
    )
    
    if response and 'choices' in response and response['choices']:
        analysis_result = response['choices'][0]['message']['content']
        return analysis_result.strip()
    else:
        return "Analysis failed due to an error."

def log_to_csv(url, transcript, analysis_result):
    """Logs the URL, transcript, and analysis result to the CSV file."""
    fieldnames = ['URL', 'Transcript', 'AI Analysis']
    file_exists = os.path.isfile(CSV_FILE_PATH)

    with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # If the file doesn't exist, write the header first
        if not file_exists:
            writer.writeheader()

        # Write the data for this particular call
        writer.writerow({'URL': url, 'Transcript': transcript, 'AI Analysis': analysis_result})

def process_call(url):
    """Orchestrates the process of handling a call: downloading, uploading for transcription, transcribing, and analyzing."""
    temp_file_name = 'temp_audio.mp3'
    try:
        download_mp3(url, temp_file_name)
        assemblyai_url = upload_audio_to_assemblyai(temp_file_name)
        transcript = transcribe_audio(assemblyai_url)
        analysis_result = analyze_transcript_with_chatgpt(transcript)
        log_to_csv(url, transcript, analysis_result)  # Log the result into the CSV
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
