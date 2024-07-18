import requests
import openai
import time
import json

# Your AssemblyAI and OpenAI API keys
ASSEMBLYAI_API_KEY = 'c34fcd7703954d55b39dba9ec1a7b04c'
OPENAI_API_KEY = 'your_openai_api_key_here'
openai.api_key = OPENAI_API_KEY

def transcribe_audio(file_path):
    headers = {"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"}
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

def analyze_transcript_with_chatgpt(transcript):
    # Enhanced analysis using ChatGPT-4
    prompt = f"Analyze the following transcript for billability criteria, quote given, and if a sale was made:\n\n{transcript}"
    
    response = openai.Completion.create(
        model="gpt-4", 
        prompt=prompt, 
        temperature=0.5, 
        max_tokens=1024,
        top_p=1.0, 
        frequency_penalty=0.0, 
        presence_penalty=0.0
    )
    
    analysis_result = response.choices[0].text.strip()
    return analysis_result

def main():
    # Assuming 'urls.txt' contains the URLs for the audio files to be transcribed
    urls = read_urls_from_file('urls.txt')  # Implement read_urls_from_file accordingly

    for index, url in enumerate(urls):
        mp3_file_name = f"audio_{index}.mp3"
        download_mp3(url, mp3_file_name)  # Implement download_mp3 accordingly
        transcription = transcribe_audio(mp3_file_name)
        
        if transcription:
            analysis_result = analyze_transcript_with_chatgpt(transcription)
            print(f"Analysis for {mp3_file_name}:\n{analysis_result}")
        else:
            print(f"Failed to transcribe {mp3_file_name}")

if __name__ == "__main__":
    main()
