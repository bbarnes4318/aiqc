import requests
import os
import time
import json
import csv
import urllib3 # Add this import for suppressing warnings

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Add this line

# ================ CONFIGURATION ================
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
OUTPUT_DIR = "C:\\Users\\Jimbo\\Desktop\\vapi-pull"
CSV_FILE_PATH = "C:\\Users\\Jimbo\\Desktop\\trans_only.csv"
# ===============================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_urls(file_name='urls.txt'):
    with open(file_name, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def download_audio(url, output_path):
    try:
        # Add verify=False to disable SSL certificate verification
        response = requests.get(url, stream=True, verify=False)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {output_path} ({os.path.getsize(output_path)} bytes)")
        return True
    except requests.exceptions.SSLError as e:
        print(f"Download failed due to SSL error: {str(e)}. Try updating certifi or checking the server's certificate.")
        return False
    except Exception as e:
        print(f"Download failed: {str(e)}")
        return False

def upload_to_assemblyai(file_path):  # CORRECT FUNCTION NAME
    try:
        headers = {'authorization': ASSEMBLYAI_API_KEY}
        with open(file_path, 'rb') as f:
            response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers=headers,
                files={'file': f}
            )
        response.raise_for_status()
        return response.json()['upload_url']
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        return None

def create_transcript(upload_url):
    try:
        headers = {
            'authorization': ASSEMBLYAI_API_KEY,
            'content-type': 'application/json'
        }
        response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            headers=headers,
            json={'audio_url': upload_url}
        )
        response.raise_for_status()
        return response.json()['id']
    except Exception as e:
        print(f"Transcription failed: {str(e)}")
        return None

def get_transcript(transcript_id):
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    
    for _ in range(12):
        try:
            response = requests.get(endpoint, headers=headers)
            data = response.json()
            if data['status'] == 'completed':
                return data['text']
            if data['status'] == 'failed':
                print(f"Transcription failed: {data.get('error')}")
                return None
            time.sleep(5)
        except Exception as e:
            print(f"Status check error: {str(e)}")
            time.sleep(5)
    return None

def save_to_csv(url, text):
    try:
        file_exists = os.path.exists(CSV_FILE_PATH)
        with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['URL', 'Transcription'])
            writer.writerow([url, text])
        print(f"Saved transcription for {url}")
    except Exception as e:
        print(f"CSV save error: {str(e)}")

def process_urls():  # CORRECT MAIN FUNCTION NAME
    urls = read_urls()
    for url in urls:
        print(f"\nProcessing: {url}")
        audio_file = os.path.join(OUTPUT_DIR, f"audio_{int(time.time())}.wav")
        
        if not download_audio(url, audio_file):
            continue
            
        upload_url = upload_to_assemblyai(audio_file)  # MATCHING FUNCTION CALL
        if not upload_url:
            os.remove(audio_file)
            continue
            
        transcript_id = create_transcript(upload_url)
        if not transcript_id:
            os.remove(audio_file)
            continue
            
        transcription = get_transcript(transcript_id)
        if transcription:
            save_to_csv(url, transcription)
            
        try:
            os.remove(audio_file)
        except:
            pass

if __name__ == "__main__":
    process_urls()  # CORRECT ENTRY POINT
    print(f"\nDone! Results saved to: {CSV_FILE_PATH}")