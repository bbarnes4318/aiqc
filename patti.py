import requests
import openai
import time
import json

# AssemblyAI and OpenAI API keys
ASSEMBLYAI_API_KEY = 'c34fcd7703954d55b39dba9ec1a7b04c'
OPENAI_API_KEY = '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'
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

# Function to transcribe audio using AssemblyAI
def transcribe_audio(file_path):
    headers = {
        "authorization": ASSEMBLYAI_API_KEY,
        "content-type": "application/json"
    }
    response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files={'file': open(file_path, 'rb')})
    audio_url = response.json()['upload_url']
    
    transcription_request = {"audio_url": audio_url}
    response = requests.post("https://api.assemblyai.com/v2/transcript", json=transcription_request, headers=headers)
    transcript_id = response.json()['id']

    while True:
        response = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
        status = response.json()['status']
        if status == 'completed':
            return response.json()['text']
        elif status == 'failed':
            return "Transcription failed"
        time.sleep(5)

def analyze_transcript(transcript):
    non_billable_reasons = []

    # Directly address each criterion for non-billability
    criteria_checks = [
        ("Lives in a nursing home", "nursing home" in transcript),
        ("Lacks a bank account, debit card, or credit card", "do NOT have an active bank account" in transcript or "do NOT have a debit card" in transcript or "do NOT have a direct express card" in transcript or "do NOT have a credit card" in transcript),
        ("Needs a power of attorney for financial decisions", "power of attorney" in transcript),
        ("Age is 81 years or older", "81 years old" in transcript or "82 years old" in transcript or "83 years old" in transcript),  # Extend this logic to cover all mentions of age over 80
        ("Unaware of call purpose regarding final expense or life insurance", "Medicare" in transcript or "free benefits" in transcript and not "final expense" in transcript and not "life insurance" in transcript),
    ]

    for reason, condition in criteria_checks:
        if condition:
            non_billable_reasons.append(reason)

    if non_billable_reasons:
        return {"Billable": False, "Reasons": non_billable_reasons}
    else:
        return {"Billable": True, "Reasons": []}

# Function to generate input for the AI model based on the transcript and a question
def generate_ai_input(transcript, question):
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Text: {transcript}\nQuestion: {question}\nAnswer:"}
    ]

# Function to analyze the AI's responses to determine if a call is billable
def analyze_responses(responses):
    non_billable_reasons = []

    # Analyzing each response according to the billability criteria
    if responses["Living Situation"].lower() == "yes":
        non_billable_reasons.append("Prospect lives in a nursing home")
    if responses["Financial Means"].lower() == "no":
        non_billable_reasons.append("Prospect does not have a bank account, debit card, or credit card")
    if responses["Power of Attorney"].lower() == "yes":
        non_billable_reasons.append("Prospect needs a power of attorney present for financial decisions")
    if responses["Age Check"].lower() == "yes":
        non_billable_reasons.append("Prospect is 81 years old or older")
    if responses["Understanding Insurance Type"].lower() == "no":
        non_billable_reasons.append("Prospect does not know they are on the call to speak with an agent regarding final expense or life insurance")

    # Determine if the call is billable based on the reasons
    if non_billable_reasons:
        billable_status = {"Billable": False, "Reasons": non_billable_reasons}
    else:
        billable_status = {"Billable": True, "Reasons": []}

    return billable_status

# Main workflow
def main():
    urls = read_urls_from_file('urls.txt')  # Assume this is a path to your file

    for index, url in enumerate(urls):
        # Download MP3 file
        mp3_file_name = f"audio_{index}.mp3"
        download_mp3(url, mp3_file_name)
        
        # Transcribe audio file
        transcription = transcribe_audio(mp3_file_name)
        
        # Analyze transcription for billability
        if transcription:
            analysis_result = analyze_transcript(transcription)
            billable_status = "Billable" if analysis_result["Billable"] else "Not Billable"
            reasons = "; ".join(analysis_result["Reasons"])
            print(f"Analysis for {mp3_file_name}: {billable_status}. Reasons: {reasons if reasons else 'N/A'}")
        else:
            print(f"Failed to transcribe {mp3_file_name}")

if __name__ == "__main__":
    main()
