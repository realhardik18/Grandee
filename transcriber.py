from dotenv import load_dotenv
import requests
import os
import time
import assemblyai as aai

load_dotenv()

API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
def upload_file(filename):
    headers = {'authorization': API_KEY}
    with open(filename, 'rb') as f:
        response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files={'file': f})
    return response.json()['upload_url']

def transcribe_audio(audio_url):
    headers = {'authorization': API_KEY, 'content-type': 'application/json'}
    data = {"audio_url": audio_url, "auto_highlights": True}
    response = requests.post('https://api.assemblyai.com/v2/transcript', json=data, headers=headers)
    return response.json()['id']

def get_transcription(transcript_id):
    headers = {'authorization': API_KEY}
    while True:
        response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
        result = response.json()
        if result['status'] == 'completed':
            return result['words']
        elif result['status'] == 'failed':
            return None
        time.sleep(5)

def generate_srt(words):
    srt_content = ""
    for i, word in enumerate(words):
        start = word['start'] / 1000
        end = word['end'] / 1000
        text = word['text']

        srt_content += f"{i+1}\n"
        srt_content += f"{format_time(start)} --> {format_time(end)}\n"
        srt_content += f"{text}\n\n"

    with open("output.srt", "w", encoding="utf-8") as f:
        f.write(srt_content)

def format_time(seconds):
    ms = int((seconds % 1) * 1000)
    s = int(seconds % 60)
    m = int((seconds // 60) % 60)
    h = int(seconds // 3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
